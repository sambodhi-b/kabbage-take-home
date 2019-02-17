# Take Home Assigment for Kabbage

## Description
Kabbage requires the ability to quickly qualify customers for a loan. To that end, Kabbage maintains web services that can score a customer against one of myriad models.
My task was to create a web service that can do two things:
- Transform a list of transactions into a feature set for a model;
- Execute a model based on the feature set, which will return a floating point
  number.

## My Solution
1. Developing Logic in Python to transform data in the raw transactional form to the feature vector required by the Predictor
2. Linking the Feature Vector to the Predictor pipeline
3. Developing a Flask Application to implement a REST API endpoint to:  
   2.1. Pass in data in the raw transactional form to transformation logic  
   2.2. Generation of Predictions by Prediction pipeline  
   2.3. Serving Predictions as JSON back to requester  
4. Containerizing the Application to enable quick and easy deployment
5. Deploying to a Kubernetes cluster to ensure scalability and uptime.

## Solution Coverage
The solution was developed till step 4.  
I could not deploy to the Kubernetes Cluster due to lack of time. A fair amount of time got consumed debugging an issue with the Prediction pipeline. Details on the issue can be found in ['initial_analysis_and_cleanup.ipynb in the initial_prep directory'](initial_prep/initial_analysis_and_cleanup.ipynb)

## Important Considerations
- How does the web service manage load?  
    It was designed to manage load by a horizontally scaled deployment where parallel nodes could be added to cater to increased load.
- How does the solution measure and optimize performance?  
    Kubernetes dashboards can be used to visually convey performance metrics regarding the deployment
- How does the web service handle and monitor resource consumption?  
    Not Implemented
- What kinds of errors does the service handle, and how does it handle them?  
    Malformed Requests are handled by the service. Currently this is actioned by a HTTP 400 response with distinct messages for common malformations. I have not found time to thoroughly analyse the exceptions possible from the Prediction pipeline, and hence they are being actioned by a HTTP 400 with a not-very-informative message.
- How do you guarantee that the service will be stable?  
    The plan was to deploy to a Kubernetes cluster which would have provided failure recovery and scalability through replication. In lieu of that implementation; the following factors will help any load balanced implementation remain stable:  
    - The service does not maintain state between requests, hence memory footprint should remain mostly invariant.
    - The Predictor pipeline should be mostly invariant in resource consumption over the predictor space
    - The web service is set-up using the lightweight Flask library.

## Usage
The Docker Image has been published to ['sambodhi/kabbage_take_home'](https://cloud.docker.com/repository/docker/sambodhi/kabbage_take_home) at DockerHub.
It can be tested on a local machine with DOcker Engine and CLI installed and configured.
To run the image on local;
```
docker run -d --name kabbage_take_home_predictor -p 5000:5000 sambodhi/kabbage_take_home:latest
```
To stop the running container;
```
docker stop kabbage_take_home_predictor
```

## Work Tracker
### Done:
1. Initial Analysis and Resolution of Issues Encountered
2. Set up logic to convert input raw data to feature set
3. Unit Tests
4. Design REST API endpoint(s)
5. Set-up Web Service
6. Containerize
7. Set-up CI Pipeline (Partially done. Automated Docker Builds on Git Push to Master through DockerHub-GitHub linkage)

### To Do:

### Backlog:
- Set-up CD Pipeline
- Deploy to Kubernetes