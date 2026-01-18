FROM eclipse-temurin:21

# Install dependencies
RUN apt-get update && apt-get install -y curl tar grep sed git python3 python3-pip jq zip \
    build-essential \
    python3-pip \
    python3-venv \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install latest Maven version
RUN MAVEN_VERSION=$(curl -s https://dlcdn.apache.org/maven/maven-3/ | grep -oP 'href="\K([0-9]+\.[0-9]+\.[0-9]+)(?=/")' | sort -V | tail -1) \
    && echo "Installing Maven version $MAVEN_VERSION" \
    && curl -fsSL https://dlcdn.apache.org/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz | tar -xz -C /opt \
    && ln -s /opt/apache-maven-$MAVEN_VERSION /opt/maven \
    && ln -s /opt/maven/bin/mvn /usr/bin/mvn

ENV MAVEN_HOME=/opt/maven
ENV PATH=$MAVEN_HOME/bin:$PATH

WORKDIR /mnt

RUN java -version && mvn -version

CMD ["mvn", "--version"]
