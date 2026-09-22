# Docker verification

Fill this in after you build and run your container (see README.md,
"Part 2 — Dockerfile"). This is how we confirm your container actually works, since an
automated grader running in a sandbox may not always have Docker-in-Docker
available.

## Build

Paste the command you ran and its final output line (the one showing the
built image ID/tag):

```
PS C:\Users\Pranav\Downloads\week06-containerize-serve_updated> docker build -t week6-detector .
[+] Building 103.8s (11/11) FINISHED                                                                                                docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                                                                0.8s
 => => transferring dockerfile: 1.28kB                                                                                                              0.1s
 => [internal] load metadata for docker.io/library/python:3.11-slim                                                                                 6.3s
 => [auth] library/python:pull token for registry-1.docker.io                                                                                       0.0s
 => [internal] load .dockerignore                                                                                                                   0.1s
 => => transferring context: 2B                                                                                                                     0.0s
 => [internal] load build context                                                                                                                   0.9s
 => => transferring context: 23.70kB                                                                                                                0.6s
 => [1/5] FROM docker.io/library/python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534                          50.0s
 => => resolve docker.io/library/python:3.11-slim@sha256:9534e5a8e315485d4061ed659af0fd78a284c015f9b73661b41d6bab25604534                           0.2s
 => => sha256:db840d086b65cf73e0feea3bd0cf11063818114e466846ae3f2b2fb1a8c2b143 14.45MB / 14.45MB                                                    8.8s
 => => sha256:f9efa1b83d065a7c5a3041582875b75d63c4ab3d4413514de8e413b51f90e91a 249B / 249B                                                          0.5s
 => => sha256:3678bb828654fcc3752f7a5eb63c5accfa00c97047252f25405285550d74a3fd 4.27MB / 4.27MB                                                      6.1s
 => => sha256:6310eb16bf4251731feab01e8f633bf5e2d75a657ccad97f420b1f83cce457be 29.79MB / 29.79MB                                                   12.0s
 => => extracting sha256:6310eb16bf4251731feab01e8f633bf5e2d75a657ccad97f420b1f83cce457be                                                          24.5s
 => => extracting sha256:3678bb828654fcc3752f7a5eb63c5accfa00c97047252f25405285550d74a3fd                                                           5.5s
 => => extracting sha256:db840d086b65cf73e0feea3bd0cf11063818114e466846ae3f2b2fb1a8c2b143                                                           6.6s
 => => extracting sha256:f9efa1b83d065a7c5a3041582875b75d63c4ab3d4413514de8e413b51f90e91a                                                           0.2s
 => [2/5] WORKDIR /app                                                                                                                              3.7s
 => [3/5] COPY requirements.txt .                                                                                                                   0.4s
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                                       30.4s
 => [5/5] COPY src/ src/                                                                                                                            0.4s
 => exporting to image                                                                                                                             10.0s
 => => exporting layers                                                                                                                             8.2s
 => => exporting manifest sha256:f34d8d3b5c8a8b7b51487b3e29b696849d0c77cfe883de0e9900e617f618d3e2                                                   0.1s
 => => exporting config sha256:077cc2ed6b6da25dad3ded541f1d4acbe129f0774f3f86d4f517c1dfcafc0667                                                     0.1s
 => => exporting attestation manifest sha256:b07b0771436374933161a3d8bc6875b3469fca2420c443ff6095e2084fe3b674                                       0.1s
 => => exporting manifest list sha256:61f70491228f033e0b518242935cc682b6686d0369be305fe139221f111d4f60                                              0.1s
 => => naming to docker.io/library/week6-detector:latest                                                                                            0.0s
 => => unpacking to docker.io/library/week6-detector:latest
```

## Run

Paste the command you used to start the container (should map a host port
to the container's 8080):

```
PS C:\Users\Pranav\Downloads\week06-containerize-serve_updated> docker run --rm -p 8080:8080 week6-detector
* Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://172.17.0.2:8080
Press CTRL+C to quit
```

## Verify

Paste the exact `curl` commands and their JSON output for both endpoints,
run against the running container (not against `python src/app.py` directly
— the point is to prove the *container* works):

```
TODO: curl http://localhost:PORT/health
TODO: <paste JSON response>

TODO: curl -F "image=@data/fixtures/camera_A_daylight/000.jpg" http://localhost:PORT/detect
TODO: <paste JSON response>
```
