FROM debian:latest AS build-env

# Install Flutter dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Download and setup Flutter
RUN git clone https://github.com/flutter/flutter.git /usr/local/flutter
ENV PATH=$PATH:/usr/local/flutter/bin
RUN flutter channel stable && flutter upgrade && flutter config --enable-web

# Copy app source code
WORKDIR /app
COPY . .

# Build the web application
RUN flutter pub get
RUN flutter build web --release

# Web server stage
FROM nginx:stable-alpine

# Copy the built web application
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Copy the custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
