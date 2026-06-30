# 1. Use an official lightweight Node.js environment
FROM node:20-alpine

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy package files first to leverage Docker's caching mechanism
COPY package*.json ./

# 4. Install all frontend project dependencies
RUN npm install

# 5. Copy the remainder of your frontend code into the container
COPY . .

# 6. Expose the standard development port (Vite typically defaults to 5173 or 3000)
EXPOSE 5173

# 7. Start the local development server
CMD ["npm", "run", "dev"]