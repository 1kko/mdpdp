# Installation

  - ## Packages
    - ### Installation

      ```
      $ sudo apt-get install python-mysqldb python-pip
      $ sudo apt-get install mariadb-server mariadb-common mariadb-client
      $ sudo pip install pymongo flask
      ```

  - ## MongoDB 
    - ### Installation

      > http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
  
      ```
      $ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
      $ echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
      $ sudo apt-get update
      $ sudo apt-get install -y mongodb-org
      $ sudo service mongod start
      ```

    - ### Configuration
      Pin this installation. (no further upgrade)
        ```
        echo "mongodb-org hold" | sudo dpkg --set-selections
        echo "mongodb-org-server hold" | sudo dpkg --set-selections
        echo "mongodb-org-shell hold" | sudo dpkg --set-selections
        echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
        echo "mongodb-org-tools hold" | sudo dpkg --set-selections
        ```

      To run mongodb server at boot,

        `$ sudo update-rc.d mongod defaults`

    - Troubleshooting

      **if you face error messages** in `/var/log/mongodb/mongdodb.log` as follows,

      Run: `$ sudo echo "smallfiles=true" >> /etc/mongod.conf`

      ```
      2015-06-16T21:53:35.452-0400 I JOURNAL  [initandlisten] journal dir=/var/lib/mongodb/journal
      2015-06-16T21:53:35.452-0400 I JOURNAL  [initandlisten] recover : no journal files present, no recovery needed
      2015-06-16T21:53:35.452-0400 I JOURNAL  [initandlisten]
      2015-06-16T21:53:35.452-0400 E JOURNAL  [initandlisten] Insufficient free space for journal files
      2015-06-16T21:53:35.452-0400 I JOURNAL  [initandlisten] Please make at least 3379MB available in /var/lib/mongodb/journal or use --smallfiles
      2015-06-16T21:53:35.452-0400 I JOURNAL  [initandlisten]
      2015-06-16T21:53:35.480-0400 I STORAGE  [initandlisten] exception in initAndListen: 15926 Insufficient free space for journals, terminating
      2015-06-16T21:53:35.480-0400 I CONTROL  [initandlisten] now exiting
      2015-06-16T21:53:35.480-0400 I NETWORK  [initandlisten] shutdown: going to close listening sockets...
      2015-06-16T21:53:35.480-0400 I NETWORK  [initandlisten] removing socket file: /tmp/mongodb-27017.sock
      2015-06-16T21:53:35.480-0400 I NETWORK  [initandlisten] shutdown: going to flush diaglog...
      2015-06-16T21:53:35.480-0400 I NETWORK  [initandlisten] shutdown: going to close sockets...
      2015-06-16T21:53:35.480-0400 I STORAGE  [initandlisten] shutdown: waiting for fs preallocator...
      ```

  - ## _(optional)_ DBMS tool installation
  
    Optionally, You may want to install gui mysql(mariadb) and mongodb management tool.

    - To Install robomongo, visit,
       > http://robomongo.org
    
    - If you want to need mysql management tool, 

       ` $ sudo apt-get install phpmyadmin`


# Data Migration
**WARNING** You might want to drop your collection **AND** table before doing this.
  * ## XML file Migration
    `$ ./importer.py <dir/path/to/xmls>`


  * ## SQL file Migration
    - Using phpMyAdmin, please refer to `import_csv_to_mysql.docx`
      1. Go to phpmyadmin page (http://localhost/phpmyadmin/), then select MEDDB/med_file.
      2. Select "Import" from tab
      3. Enter following:
         * skip rows:1
         * Type: CSV
         * Column Names: `MD5_Key,File_Name,Result_Number,Virus_Name,AV_Scan,MDP_Rule,Sign_Credit,REPORT_PC_Count,Saved_Size,File_Tag,CTIME`

    - For DEMO, you may just import things as follows
      ```
      $ mysql -uroot -p < CREATEUSER.sql
      $ mysql -uroot -D MEDDB -p < MEDDB.sql
      ```
    - To increase php max upload file size, change to following values in `/etc/php5/apache2/php.ini` 
      ```
      post_max_size = 1024M
      upload_max_filesize = 1024M
      ```
      then run: `$ sudo service apache2 restart`


 * ## Behavior JSON Migration
    - use `mongoimport`:
      ```
      $ mongoimport --db=MDP behavior.json
      ```


# Start Web Server
just run `$ ./startweb.py`


# Usage
use web browser, go to url: **http://localhost:5000**

# Performance
To increase search speed, it's better to create index in mongodb.
However, creating index may take long time.

```
$ mongo
MongoDB shell version: 3.0.4
connecting to: test
> 
> use MDP
switched to db MDP
>
> db.behavior.createIndex({"$**":"text"},{name:"TextIndex"})
{
  "createdCollectionAutomatically" : false,
  "numIndexesBefore" : 1,
  "numIndexesAfter" : 2,
  "ok" : 1
}
> 

```
