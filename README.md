<h1 align="center">
NTUA - Distributed Systems
</h1>

<h3 align="center">
A simple blockchain system
</h3>


## The noobcash project

Noobcash is a decentralized cryptocurrency system. Every node is a miner and each transaction made in the system is verified by a network of nodes and then added to a block, which, when full, is added to the Blockchain. The nodes in this system communicate via a peer-to-peer network using cryptography for the verification processes. 


## Setup/Usage

- Install and open the Docker Desktop App
  
- Setup the environment

    ```
    $ docker compose build
    ```

- Run the experiment for the specified parameters (i.e number of participants = 5, difficulty = 4, capacity = 1).

    ```
    $ docker compose -f compose/p5-d4-c1-docker-compose.yml up
    ```

    

    ```
    $ python  
    usage: rest.py [-h] -p P -n N -capacity CAPACITY [-bootstrap]

- Alternative: Run all the experiments with 5 nodes (with all the possible combinations of the given parameters).

    ```
    $ ./run_all_5_nodes.py
    ```

    > **_NOTE:_** Before running the ./run_all_5_nodes.py command, the lines 195-195 of the source/rest.py file should be uncommented.
    
    ```
      #sleep(100)
      #_thread.interrupt_main()
    ```
   
- Run a CLI client:

     ```
     $ docker exec -it [container_name]
     ```


    usage: client.py [-h] -p P

    CLI client of noobcash.

    optional arguments:
      -h, --help  show this help message and exit

    required arguments:
      -p P        port to listen on
    ```

    > **_NOTE:_** Each execution of the code above represents a CLI client for the corresponding node at the specified port P.
    
    **Cli Client Demo**
    ![client-demo](etc/client-demo.gif)

- Run the webapp:

    1. Update the local settings [file](webapp/webapp/local_settings.py)
    2. `$ python webapp/manage.py makemigrations`
    3. `$ python webapp/manage.py migrate`
    4. `$ python webapp/manage.py shell`

        Type the following in the interactive console:

        `exec(open('db_script.py').read())`

        which executes a script to populate the database with the default settings for the nodes.

        See [here](webapp/nodes.json) for the default settings.
    5. `$ python webapp/manage.py createsuperuser`
        
        Save the credentials you used because you will need them to log in to the webapp.
    6. `$ python webapp/manage.py runserver`
    
        You can visit the webapp at http://127.0.0.1:8000


## Technologies used

1. The rest api is written in Python 3.6 using the following libraries: 
    - Flask
    - Flask-Cors
    - pycryptodome
    - requests
    - urllib3
2. The webapp is developed using Django 3.0.4 and Python 3.6

## Evaluation of the system

We evaluate the performance and the scalability of Noobcash by running the system in [okeanos](https://okeanos-knossos.grnet.gr/home/) and perform from each node 100 transcations to the system. The transactions are placed in `/test/transactions` and the scipt for executing them in `test/tester.py`. 


- Performance of the system

 <p float="left">  
    <img src="test/plots/throughput_n5_c.png" width="420"/>
  <img src="test/plots/block_n5_c.png" width="420"/>
 </p>
 
 - Scalability of the system
 
  <p float="left">  
    <img src="test/plots/scalability_t.png" width="420"/>
  <img src="test/plots/scalability_b.png" width="420"/>
 </p>





## Project Structure

- `src/`: Source code of the rest backend and cli client.
- `test/`: Files regarding the evaluation of the system.
- `webapp/`: Files about the web app.

## Contributors

Developed by

<p align="center">
    <a href="https://github.com/PanosAntoniadis"> <img src="etc/antoniadis.png" width="10%"></a>  <a href="https://github.com/Nick-Buzz"><img src="etc/bazotis.png" width="10%"></a>  <a href="https://github.com/ThanosM97"><img src="etc/masouris.png" width="10%"></a>
<p>
    
as a semester project for the Distributed Systems course of NTUA ECE.
