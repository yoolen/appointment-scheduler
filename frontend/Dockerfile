# Use Node.js 18 Alpine image (much smaller than regular Node image)
# Alpine Linux is a security-oriented, lightweight Linux distribution
FROM node:18-alpine

# Set working directory inside container
WORKDIR /app

# Copy package.json and package-lock.json first (if exists)
# This creates a separate Docker layer for dependencies
# If package.json doesn't change, npm install layer can be cached
COPY package*.json ./

# Install Node.js dependencies
# This runs in the dependency layer, separate from source code
RUN npm install

# Copy application source code
# This happens after npm install so code changes don't invalidate dependency layer
COPY . .

# Document that this container will listen on port 3000
# This is informational only - doesn't actually publish the port
EXPOSE 3000

# Default command to run the Vue development server
# npm run dev: Runs the Vite development server
# --: Separates npm arguments from Vite arguments
# --host 0.0.0.0: Bind to all interfaces (required for Docker networking)
# --port 3000: Listen on port 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]