# µGrowthDB: A database interface and GUI for the collection and analysis of microbial growth data

This repository contains the code implemented during my master's thesis in Bioinformatics at KU Leuven with the colaboration of
the Laboratory of Microbial Systems Biology located at the Rega Institute in Leuven, Belgium.

**Objective**

The main objective of this thesis was to develop a database of microbial growth data (µGrowthDB) and a web application interface graphical user interface GUI. µGrowthDB was developed to be a community-oriented resource enabling researchers to share, retrieve, and visualize growth data.

**Structure of this repository**

This repository was initially forked from  [Julia Casados's repository](https://github.com/jcasadogp/bacterial_growth), who previously worked on the development of the database schema.

There are three main folders:
1. **app:** It contains all the source code of the web application GUI.
2. **env:** It includes the yml file required to install all of the python libraries used.
3. **src:** with all the code related to the database schema and functions to parse and access data from and into the database.

> [!TIP]
> New to Github and don't how to fork this repository? Go and check all of the different [Github tutorial](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo).

## Table of contents
1. [Environment set up](#1)
2. [Creation of the database](#2)
3. [Init the app](#3)
3. [Additional Dependencies](#4)
4. [Demos](#5)


## 1. Environment set up <a name="1"></a>
First, you need to set up the environment that contain all the packages that will be used by application. To do so, run the following commands:
````
cd envs/
conda env create -f environment.yml
````
> [!NOTE]
> In case of errors while installing the environment, it could be related to the following issues:
> * Conda Version: Make sure you are using an up-to-date version of Conda. You can update Conda using the command: `conda update conda`.
> - Package Conflicts: Sometimes, package dependencies conflict with each other. You might need to edit the `environment.yml` file to specify compatible versions or remove conflicting packages.
> * Operating System Compatibility: Certain packages might not be compatible with your operating system. Check the documentation of the problematic package for OS-specific instructions or alternatives.

## 2. Create the database <a name="2"></a>

µGrowthDB is a MySQL database, in order to run the app you need first to have the database locally in your machine.

### 1. Install MySQL Server

Go to [MySQL Server](https://dev.mysql.com/downloads/mysql/) and download the program. Follow the installation instructions provided for your specific OS.

### 2. Create a local version of µGrowthDB

Once MySQL is installed and running, you need to create the µGrowthDB database. Open the MySQL command-line client (usually comes with the installation of MySQL Server).Log in as the root user or another user with the necessary privileges:

````
mysql -u root -p
````

It will ask for your password which you had to create during the installation. Once logged in, type the command `source` plus the path to the database schema:

````
source ../bacterial_growth/src/sql_scripts/create_db.sql;
````
> [!NOTE]
> Make your the provided path is compleate and correct, this can change depending on where are you located.

Once the datase is created different functions and scripts within the code access it in order to populate and retrieve data. For this reason, you need to have under the `app/.streamlit` folder a file called `secrets.toml` with the following:

```yaml
[connections.BacterialGrowth]
dialect = "mysql"
username = "yourusername"
password = "yourpassword"
host = "yourhost"
database = "BacterialGrowth"
```
For more information go to the [Streamlit's documentation](https://docs.streamlit.io/develop/concepts/connections/secrets-management).

> [!IMPORTANT]
> Secrets are private! Do not forget to add the path to the secrets.toml to your `.gitignore`.


### 3. Populate the metabolite table from the MCO Ontology and the taxa table from NCBI taxonomy

This database also includes metabolite names and IDs gathered from the MCO ontology, as well as taxa information from the NCBI taxonomy database.

#### 1. Populate the Metabolites table

To populate this table into the database go `src/sql_scripts` and run the `populate_metadb.py` with the following command:

````
python populate_metadb.py
````

#### 2. Populate the Taxa table

From [JensenLab FTP](https://download.jensenlab.org) we download the `organisms_dictionary.tar.gz` file. 

In the `METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv` file there is a list of *small* Eukaryotes.
Of course this could be also be updated from time to time. 

We keep the `organism_entities.tsv` and `organism_groups.tsv` files in the same directory with the `create_groups.pl` script and run it to build the `growthDB_groups.tsv`

```bash
./filter_unicellular_ncbi.awk  METdb_GENOMIC_REFERENCE_DATABASE_FOR_MARINE_SPECIES.csv  database_groups.tsv  >  growthDB_unicellular_ncbi.tsv
```

<!-- ```bash
file1="growthDB_unicellular_ncbi.tsv"
file2="names.dmp"
awk -F "\t"  'NR == FNR { file1_entries[$1] = 1; next } $1 in file1_entries { print $1, $3 }' "$file1" "$file2" > unicellular_ncbi_id_name.tsv
``` -->

Now we need to map the NCBI Taxonomy Ids to taxa names.
Yet, for a single NCBI Taxonomy Id we may have more than 1 names. 
To address this and make the dynamic search easier, we will use the `organisms_preferred.tsv` as well. 

First, we make an overall file with NCBI Taxonomy Ids and their corresponding preferred names:

```bash
file1="organisms_entities.tsv"
file2="organisms_preferred.tsv"
awk -F "\t" 'NR == FNR { file1_org_ids[$1] = 1; file1_ncbi_ids[$1] = $3; next } $1 in file1_org_ids { print file1_ncbi_ids[$1], $2 }' "$file1" "$file2" > ncbi_ids_preferred_names.tsv
sed -i 's/ /\t/' ncbi_ids_preferred_names.tsv
```


Now, we keep the NCBI Taxonomy Ids returned from the `filter_unicellular_ncbi.awk` script which are present in the `organisms_entities.tsv`:
```bash
file1="growthDB_unicellular_ncbi.tsv"
file2="organisms_entities.tsv"
awk -F "\t"  'NR == FNR { file1_entries[$1] = 1; next } $3 in file1_entries { print $3 }' "$file1" "$file2" > unicellular_ncbi_ids.tsv
```

Finally, we get only NCBI Taxonomy Ids along with their corresponding preferred names of the unicellular taxa:
```bash
file1="unicellular_ncbi_ids.tsv"
file2="ncbi_ids_preferred_names.tsv"
awk 'NR == FNR { file1_ncbi_ids[$1] = 1 ; next } $1 in file1_ncbi_ids { print $0 }' "$file1" "$file2" > unicellular_ncbi_ids_preferred_names.tsv
```

Once completed, we may load the `unicellular_ncbi_ids_preferred_names.tsv` in the `Taxa` table in the `BacterialGrowth` database.
```bash
mv unicellular_ncbi_ids_preferred_names.tsv /var/lib/mysql-files
mysql --local-infile=1 -u <username>  -p
```

and now

```sql
mysql> use BacterialGrowth;
mysql> LOAD DATA INFILE '/var/lib/mysql-files/unicellular_ncbi_ids_preferred_names.tsv' INTO TABLE Taxa FIELDS TERMINATED BY '\t' LINES TERMINATED BY '\n';

```


## 3. Init the app <a name="3"></a>
Once all of the above is ready, to run the application type the following command:

```bash
streamlit run app.py
```
Did you get this error?

```bash
    raise OSError(errno.ENOSPC, "inotify watch limit reached")
OSError: [Errno 28] inotify watch limit reached
```
Try the following command instead.

```bash
streamlit run app.py --server.fileWatcherType none
```

> [!NOTE]
> Remember to be inside the `app` folder or wherever your `app.py` script is located.


## Dependencies <a name="4"></a>

```bash
pip install -U Flask-SQLAlchemy
```
The `Flask-SQLAlchemy` is required for the `st.connection` to work. 


```bash
pip install streamlit-tags
```
for the tags in the upload page.

`openpyxl>=3.1.0`

## Demos <a name="5"></a>

