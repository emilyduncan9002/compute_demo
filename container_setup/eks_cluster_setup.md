# Let's Set Up a K8s Cluster
<!-- START doctoc -->
<!-- END doctoc -->

**Table of Contents**

- [Helpful Links](#helpful-links)
- [Steps to Create Juice Shop](#steps-to-create-juice-shop)
- [Steps to Deploy Defender](#steps-to-deploy-defender)
- [Demo Scenarios](#demo-scenarios)
    - [Block New Pods with Critical Vulnerabilities](#block-new-pods-with-critical-vulnerabilities)
    - [Fail Builds with Critical Vulnerabilities](#fail-builds-with-critical-vulnerabilities)
    - [Block Cryptominer with Runtime Policy](#block-cryptominer-with-runtime-policy)
    - [Block malware download](#block-malware-download)
    - [Prevent Binaries with Suspicious ELF headers](#prevent-binaries-with-suspicious-elf-headers)
    - [Prevent explicilty denied processes](#prevent-explicilty-denied-processes)
- [Clean Up Resources](#clean-up-resources)

## Helpful Links
- https://dev.to/aws-builders/aws-eks-setup-cluster-and-deploy-owasp-juice-shop-214j
- https://kubernetes.io/docs/tasks/debug/debug-application/get-shell-running-container/


## Steps to Create Juice Shop
1. Launch new EKS Cluster (this takes some time)

    ```
    eksctl create cluster --name my-cluster --region us-east-1 --profile personal
    ```

2. Check if cluster is ready

    ```
    aws eks list-clusters --region us-east-1 --profile personal
    ```

3. Update kubeconfig so we can use kubectl
    
    ```
    aws eks update-kubeconfig --name my-cluster --region us-east-1 --profile personal
    ```

4. Validate context
    
    ```
    kubectl config current-context
    ```

5. Validate that nodes are ready
    
    ```
    kubectl get nodes
    ```

6. Create namespaces
    
    ```
    kubectl apply -f namespaces.yaml
    ```

7. Create kubernetes deployment and service for juice shop

    ```
    kubectl create -f juice-shop.yaml --namespace=juice-shop
    ```

8. Validate pod is running
    
    ```
    kubectl get pods
    ```

9. Validate Service is functional on port 8000
    
    ```
    kubectl get svc juice-shop
    ```

10. Expose the service on localhost
    
    ```
    kubectl port-forward svc/juice-shop 8080:8000
    ```
- Note: Pods will not appear in radar/containers because defender is not deployed

## Steps to Deploy Defender
1. Get Defender yaml
    - Manage -> Defenders -> Deploy -> Defenders -> Orchestrator = Kubernetes
    - Enter the cluster name created above
    - Download yaml in step 15.b
2. Create daemonset in cluster
    
    ```
    kubectl create -f juice-daemonset.yaml --namespace=twistlock
    ```

- Note: Pods should appear in radar/containers view now


## Demo Scenarios
- Block new pods with critical vulnerabilties
### Block new pods with critical vulnerabilities
- Set Up
    - Create a collection that is scoped to the cluster we created
    - Create a Vulnerability Policy to block if critical vulnerability is identified
1. Create Collection
    - Manage -> Collections and Tags -> Add Collection
    - Enter Name
    - Enter juice* in Namespaces field
2. Create Vulnerability Rule
    - Defend -> Vulnerabilities -> Images -> Deployed -> Add Rules
    - Enter Rule Name
    - Enter scope = Name of Collection Created
    - Set Block Threshold to Critical
    - Block grace period = All Severities for 60 days
    - Enable 'Apply Rule only when vendor fixes are available'
    - Choose summary or detailed report = Detailed

3. Scale juice-shop deployment to 2. Note pods should not enter running status
    
    ```
    kubectl scale deployment juice-shop --replicas=2 -n juice-shop
    ```

4. Validate pod status = RunContainerError
    
    ```
    kubectl get pods -n juice-shop
    ```

5. Check reason for pod failure
    
    ```
    kubectl describe pod [name of any pod] -n juice-shop
    ```
6. Take note of Error and CVEs in scan results
7. Add exceptions for critical CVEs in Juice Shop Rule
    - Defend -> Vulnerabilities -> Juice Shop Rule -> Add Exception
    - Ignore noted CVEs and set expiration date
8. Restart pods
    
    ```
    kubectl scale deployment juice-shop --replicas=2 -n juice-shop
    ```

9. Validate that pod that was previously blocked is now running
    
    ```
    kubectl get pods -n juice-shop
    ```

This demonstrates:
- the blocking capabilities of the Vulnerability Policies when trying to create new pods
- the ability to add exceptions to rules, and the real time impact to what the defender blocks

### Fail Builds with Critical Vulnerabilities
- Set Up
    - [Install twistcli](https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin-compute/tools/twistcli)
        - Recommend using copy instead of download
        - For mac users: after running the curl command, run "chmod a+x ./twistcli"
    - [Install Docker Engine](https://docs.docker.com/engine/install/)
    - To scan any image, it must be present in local Docker Hub
        - If image is available on public docker registry, use "docker pull [image name]"
1. Create Collection
    - Manage -> Collections and Tags -> Add Collection
    - Enter Name
    - Enter bkimminich/juice-shop:latest in the Images field
2. Create Vulnerability Rule
    - Defend -> Vulnerabilities -> Images -> CI -> Add Rules
    - Enter Rule Name
    - Enter scope = Name of Collection Created
    - Set Failure Threshold to Critical
    - Grace period = All Severities for 60 days
    - Enable 'Apply Rule only when vendor fixes are available'
    - Choose summary or detailed report = Detailed
3. In your terminal, run the twistcli scan

    ```
    twistcli images scan bkimminich/juice-shop --address [Path to Console] --user=[Your Access Key] --password=[Your Secret Key] --details 
    ```
    - To Find Path: Login to Console -> Compute -> Manage -> System -> Copy "Path to Console"

4. Point out that the scan shows all vulnerabilities and compliance issues in the image (set by alert threshold in vulnerability and compliance CI policy)
    - Point out that you can see the CVEs, impacted packages, fix status, and what caused the failure (Triggered Failure = Yes)
5. Add exceptions for critical CVEs in Juice Shop Rule
    - Defend -> Vulnerabilities -> CI -> uice Shop Rule -> Add Exception
    - Ignore noted CVEs and set expiration date
6. Run twistcli scan again
    - Point out that now that the exceptions have been added, the critical vulnerabilities no longer cause a build failure (Triggered Failure = No)

This demonstrates:
- the ability to integrate with build processes, and to fail builds if policies are violated
- the ability to add exceptions to rules, and the real time impact to what twistcli fails

### Block Cryptominer with Runtime Policy
1. Create Collection
    - Manage -> Collections and Tags -> Add Collection
        - Enter Name
        - Enter juice* in Cluster field
2. Create Runtime Policy
    - Defend -> Runtime -> Container Policy -> Add Rule
        - Enter Rule Name
        - Enter scope = Name of Collection Created
        - Set Rule to Block if Crypto miner is identified
            - Process -> Denied and fallback
        - Save Rule
3. Create pod with cryptominer

    ```
    kubectl run cryptominer --image=rcmelendez/xmrig
    ```

4. In Console, view event that was generated
    - Monitor -> Events -> Container Audits
        - Select image used to create crypto miner pod
        - View Audit Data
        - Point out the Effect, which should be blocked
        - Point out the Event type, which should be crypto miner process
5. View the Incident that was created
    - Monitor -> Runtime -> Incident Explorer
        - Select crypto miner event that imacted the image used to create the crypto miner
        - Select View live forensic
        - Point out the Runtime audit event
        - Point out when the Incident is created
6. Demonstrate that forensic data can be exported
    - Select Export
7. Demonstrate that Incident can be archived
    - Under Actions, select the File Box

This demonstrates:
- the capability to block cryptominers from being created and running
- the ability to capture and visualize forensic data that can be utilized in response activities

### Block malware download
1. Ensure Wildfire is enabled
    - Manage -> System -> Wildfire
2. Create Collection
    - Manage -> Collections and Tags -> Add Collection
        - Enter Name
        - Enter juice* in Cluster field
3. Create Runtime Policy
    - Defend -> Runtime -> Container Policy -> Add Rule
        - Enter Rule Name
        - Enter scope = Name of Collection Created
        - Set Rule to Block if Malware is identified
            - Anti-malware -> Use WildFire malware analysis
        - Save Rule
4. Create pod to download sample malware document

    ```
    kubectl apply -f https://k8s.io/examples/application/shell-demo.yaml
    ```
5. Download file
    
    ```
    kubectl exec --stdin --tty shell-demo -- curl -L http://wildfire.paloaltonetworks.com/publicapi/test/elf -o /tmp/malware-sample
    ```

6. In Console, view event that was generated
    - Monitor -> Events -> Container Audits
        - Select image used to download the file
        - View Audit Data
        - Point out the Effect, which should be blocked
        - Point out the Event type, which should be Filesystem WildFire Malware
7. View the Incident that was created
    - Monitor -> Runtime -> Incident Explorer
        - Select Malware event that imacted the image used to download the file
        - Select View live forensic
        - Point out the Runtime audit event
        - Point out when the Incident is created
8. Demonstrate that forensic data can be exported
    - Select Export
9. Demonstrate that Incident can be archived
    - Under Actions, select the File Box

This demonstrates:
- the capability to block malware downloads
- the ability to capture and visualize forensic data that can be utilized in response activities

### Prevent Binaries with Suspicious ELF headers
1. Create Collection
    - Manage -> Collections and Tags -> Add Collection
        - Enter Name
        - Enter juice* in Cluster field
2. Create Runtime Policy
    - Defend -> Runtime -> Container Policy -> Add Rule
        - Enter Rule Name
        - Enter scope = Name of Collection Created
        - Set Rule to Prevent if binaries with suspicious elf headers are identified
            - File System -> Denied & fallback
        - Save Rule
3. Create pod to download sample malware document

    ```
    kubectl apply -f https://k8s.io/examples/application/shell-demo.yaml
    ```

4. Curl dropbear

    ```
    kubectl exec --stdin --tty shell-demo -- curl -L https://github.com/Miraje/dropbear/blob/master/dropbear\?raw\=true -o dropbear-arm-32
    ```

5. In Console, view event that was generated
    - Monitor -> Events -> Container Audits
        - Select image used to download the file
        - View Audit Data
        - Point out the Effect, which should be Prevent
        - Point out the Message, which should state 'Suspected malicious ELF file'...
6. View the Incident that was created
    - Monitor -> Runtime -> Incident Explorer
        - Select Suspicious Binaary event that imacted the image used to download the file
        - Select View live forensic
        - Point out the Runtime audit event
        - Point out when the Incident is created
7. Demonstrate that forensic data can be exported
    - Select Export
8. Demonstrate that Incident can be archived
    - Under Actions, select the File Box

This demonstrates:
- the capability to prevent suspicious binaries from being created
- the ability to capture and visualize forensic data that can be utilized in response activities

### Prevent explicilty denied processes
1. Create Collection
    - Manage -> Collections and Tags -> Add Collection
        - Enter Name
        - Enter juice* in Cluster field
2. Create Runtime Policy to Block when ls is executed
    - Defend -> Runtime -> Container Policy -> Add Rule
        - Enter Rule Name
        - Enter scope = Name of Collection Created
        - Set Rule to Block if ls is executed
            - Processes -> add "ls" to Processes
        - Save Rule
3. Create pod to download sample malware document

    ```
    kubectl apply -f https://k8s.io/examples/application/shell-demo.yaml
    ```

4. Exec into pod
    
    ```
    kubectl exec --stdin --tty shell-demo -- /bin/bash 
    ```

5. Execute ls
    
    ```
    ls
    ```

6. In Console, view event that was generated
    - Monitor -> Events -> Container Audits
        - Select image used to download the file
        - View Audit Data
        - Point out the Effect, which should be Block
        - Point out the Event type, which should be Processes/Explicitly Denied Processes
7. View the Forensics data
    - Select forensics
    - Point out the Runtime audit event
    - Point out when the Process was spawned
8. Demonstrate that forensic data can be exported
    - Select Export

This demonstrates:
- the capability to prevent defined processes
- the ability to capture and visualize forensic data that can be utilized in response activities




## Clean Up Resources
1. Delete when finished

    ```
    eksctl delete cluster --name my-cluster --region us-east-1 --profile personal
    ```