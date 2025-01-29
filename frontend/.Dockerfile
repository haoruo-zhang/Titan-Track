FROM node:18

WORKDIR /app

# 拷贝 package.json 和 yarn.lock
COPY package.json yarn.lock ./

# 使用 Yarn 安装依赖
RUN yarn install

# 拷贝项目文件
COPY . .

EXPOSE 5173

CMD ["yarn", "dev"]

