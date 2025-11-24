# Oregon State Univeristy HPC Star CCM+ Data Acquisition 

The below document is inteded to get you started on using the OSU HPC server to run
STAR-CCM+ for data acquisition. Future revisions will include the (currently in development)  automated data collection scripts.

## Getting OSU HPC Access

Follow the instructions on [it.engineering.oregonstate.edu/hpc](https://it.engineering.oregonstate.edu/hpc), under "Getting Started With The COE High Performance Computing Cluster"

## Running STAR-CCM+ on OSU HPC

## Via Web UI

After you have OSU HPC Access, to access the Web UI you need to either
- Be on the OSU Campus wifi
    - This can only be done in person
- Activate the OSU VPN
    - See [OSU VPN](https://technology.oregonstate.edu/services/vpn) for details
- Use a tool to pass traffic
    - On linux, you can use: `sshuttle -r flip 0/0 -vv --dns`

After this, you will be able to access the Web UI at [submit.hpc.engr.oregonstate.edu](http://submit.hpc.engr.oregonstate.edu/)

From there, login with onid credentials

### Checking Available resources

Now, you need to request resources. You can request them blindly, but you may want to check and see what's available first so that you don't end up waiting literal days.

First, familiarize yourself with the available partitions in [it.engineering.oregonstate.edu/hpc/slurm-howto](https://it.engineering.oregonstate.edu/hpc/slurm-howto) under "Summary of partitions". These are the different groups the resources are reserved for. 

Note that only some of the partitions have access to GPUs, we are still testing whether they are helpful for batch simulations, but the GPU partitions are always harder to get resources on. The GPU partitons generally have "dgx" in their name. 

Generally everyone has access to Share and Preempt partitions. It can be harder to get resources on share, but jobs on preempt can be "preempted" by a higher priority job at any time (this will cancel your session and if the simulation wasn't done and you hadn't exported the data, you will lose everything). Generally, if you have access, the other partitions are easier to get resoruces on. For example, if you're in EECS, there is a partition labeled "EECS" that is generally very open. 

When requesting a STAR-CCM+ session, it will only show you the partitions you have access to.

To check available resources, under the top bar click "Clusters", then ">_HPC Cluster Shell Access". From there you can run `sinfo` or `nodestat PARTITION_NAME`. The first will tell you the status of all of the partitions, the second will tell you the available resources on each node of the partition. **When requesting resources, you want to ensure the partition you're requesting from has a node with the resources you're requesting available using `nodestat`.**

### Requesting resources

We will run STAR-CCM+ from the STAR-CCM+ button in the Interactive Apps menu. After you click that button, it will take you to the page to request resources. 

 - First, choose STAR-CCM+ version. It may not default to the latest (the highest version on the HPC may not be the latest version, if you need the latest version, contact the HPC manager Robert Yelle).

 - Next, choose your partition. This should be the partition you checked in the "Checking Available resources" section of this guide. For now we recommend avoiding preempt.

 - You can likely leave the "Account" option alone.

 - For hours, always request more (double) than you think you need. You can always end a session early, but when you run out of time there's no extensions and if you haven't exported the data, everything is lost. We recommend a minimum of twelve hours. Note though that the length you request may impact your queue time before you get resources. Though this generally is only seen when you request multiple days, there isn't much difference below 12 hours.

 - We recommend only requesting one node, but you can request 2. Generally inter-node communication is extremely slow (in the order millions of CPU cycles).

 - For cores, for quick jobs we recommend less than 32 cores as it can be hard to find a node with more than 32 cores available. Even if they are available, we find the queue to be longer when you request more than 32 cores. Note that your resource limits are cumulative, so you can just request multiple sessions if you want to run more simulations.

 - GPUs can only be requested on a partition with GPUs. We are still testing if they are helpful, but requesting them can sometimes increase your queue time.

 - For memory, do more than you think, but STAR-CCM+ is not that memory heavy. You can do 128g if you want, but 32g is probably already than enough by several times. Make sure to append "g" to your number as otherwise it requests in megabytes.

 - You can request a specific node, such as the one you found free in "Checking Available resources", but it likely doesn't matter.

After everything is ready click "Launch". Then you will be taken to the "My Interactive Sessions" page. It will then say Queueing for a bit, then Preparing, then Running. If you requested your resources correctly and ensured there was space avaiable it should take from 30 seconds to less than 5 minutes. Sometimes it doesn't update even though it's ready, so refresh the page to check its status.

### Using the remote desktop

First note the two sliders. Remote Desktops have high latency as it is reording the screen, sending it to you, and then sending your inputs back. To decrease that latency some, we recommend setting Compression around 6 and Image Quality around 2. You can experiment with values if you find the quality too low or the latency/lag too high.

Now, you can click "Launch STAR_CCM+" and then fullscreen STAR-CCM+ after it loads.

From there it should be just like using STAR-CCM+ on your desktop, but if any issues arise let us know by submitting an issue to [github.com/SCRT-Capstone-2025-26/SCRT_Rocket_SIM](https://github.com/SCRT-Capstone-2025-26/SCRT_Rocket_SIM) and we will update the guide with more information about the TurboVNC remote desktop or otherwise help resolve your issue.



### Resource Limits

These limits are cumulative on all running jobs, so we suggest you only use one node per job as multi-node jobs are much slower and you can just run multiple jobs instead.

Limits depend on your partition. They can be found in [it.engineering.oregonstate.edu/hpc/slurm-howto](https://it.engineering.oregonstate.edu/hpc/slurm-howto) under "Summary of partition limits".

For the Share partition, your limits as of November 2025 are: 
- CPU: 512 CPU days per week. So 512 CPUs for 1 day a week or 73 CPUs for the entire week. 
- GPU: 2 GPU days per week.
- RAM: 1536 GB days per week.
- Storage: 15 GB

Note that while your storage is fixed, there is additional temporary shared storage of up to 1 TB. This can be accessed under 
```/nfs/hpc/share/YOUR_ONID```
only while in the HPC servers. To transfer this to your computer you will need to use something like `scp` (Secure Copy Protocol). Note that this storage may be occasionally deleted, but you should get a notification a few days before it is deleted.


## Via CLI

Coming soon

## Using STAR-CCM+

Coming soon. For now, see offical tutorials.