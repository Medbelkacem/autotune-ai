FROM node:20-alpine AS deps
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@9 --activate
COPY package.json pnpm-lock.yaml* ./
COPY ../../packages/shared-schemas/typescript /packages/shared-schemas/typescript
RUN pnpm install --frozen-lockfile || pnpm install

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable && corepack prepare pnpm@9 --activate
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build
EXPOSE 3000
CMD ["pnpm", "start"]
