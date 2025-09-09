# ---- Base Stage ----
FROM node:18-alpine AS base
WORKDIR /app
COPY package.json yarn.lock* ./
RUN yarn install --frozen-lockfile

# ---- Builder Stage ----
FROM base AS builder
COPY . .
RUN yarn build

# ---- Production Stage ----
FROM node:18-alpine AS production
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs
EXPOSE 3000

CMD ["yarn", "start"]