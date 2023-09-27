<h1 align="center">
NTUA - Distributed Systems <br/><br/>
Noobcash
</h1>

<p align="center">
    <br>
    <img src="etc/logo.jpg" alt="Noobcash" width="200"/>
    <br>
<p>

<h2 align="center">
A simple blockchain system
</h2>


## The noobcash project

Noobcash is a decentralized cryptocurrency system. Every node is a miner and each transaction made in the system is verified by a network of nodes and then added to a block, which, when full, is added to the Blockchain. The nodes in this system communicate via a peer-to-peer network using cryptography for the verification processes. 


## Setup / Usage

- Install and open the Docker Desktop App
  
- Setup the environment :

    ```
    $ docker compose build
    ```

- Run the experiment for the specified parameters (i.e. number of participants = 5, difficulty = 4, capacity = 1) :

    ```
    $ docker compose -f compose/p5-d4-c1-docker-compose.yml up
    ```

- Alternative: Run all the experiments with 5 nodes (with all the possible combinations of the given parameters) :

    ```
    $ ./run_all_5_nodes.sh
    ```

    > **_NOTE :_** Before running the ./run_all_5_nodes.py command, the lines 189-190 of the source/rest.py file should be uncommented. Those two lines are the following :
     ```
    #sleep(100)
    #_thread.interrupt_main()
     ```
   
- Run a CLI client (i.e client1) :

     ```
     $ docker exec -it [container_name] bash
     ```

    **_Example :_** ```  $docker exec -it client1 bash```

    In the client-terminal, run :
    
    ```
     $ python cli/main.py [argument]
     ```

    Where available arguments are the following:
    - -h, --help   
    - t [recipient_address] [amount]
    - view
    - balance

    **_Example :_** ```  $python cli/main.py balance```


- VIsit the browser page : http://localhost:8000/docs (while the program is running).
    - Port 8000: bootstrap
    - Port 8001: client1
    - Port 8002: client2
    - etc...

