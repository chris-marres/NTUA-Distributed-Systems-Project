import os

folder_path = "outputs-5-nodes"
#thr_5 = []
#bl_5  =[]

for file in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file)
    with open(file_path, 'r') as f:        
        total_throughput = 0
        counter_throughput = 0
        total_blocks = 0
        counter_blocks = 0 
        for line in f:
            line = line.split(" ")
            # Throughput: value
            if (line[0] == "Throughput:"):
                total_throughput += float(line[1])
                counter_throughput += 1
            # Block time: value    
            elif (line[0] == "Block"):
                total_blocks += float(line[2])
                counter_blocks += 1
        throughput = total_throughput /counter_throughput
        block_time = total_blocks /counter_blocks
        #thr_5.append(throughput)
        #bl_5.append(block_time)

        
        print(f"\n\n#-#-#-#-#-#    FILE: {file}    #-#-#-#-#-#\n")
        print("Throughput of the system:", throughput)   
        print("Average block time:", block_time)  
        #print("\n#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
