# =============================================================================
# SentryView Frontend — React (CRA) → nginx
# Tag convention: jorahone/sentryview-frontend:latest
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json ./
RUN npm ci --include=dev

# Copy source and build
COPY . .
RUN npm run build

# ── Production stage ────────────────────────────────────────────────────────
FROM nginx:alpine

# Copy built files (CRA outputs to /app/build)
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user
RUN addgroup --system --gid 1001 sentryview && \
    adduser --system --uid 1001 --ingroup sentryview --no-create-home sentryview && \
    chown -R sentryview:sentryview /usr/share/nginx/html /var/cache/nginx /var/run && \
    chmod -R 755 /usr/share/nginx/html

USER sentryview

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD wget --spider -q http://127.0.0.1/ || exit 1

LABEL org.opencontainers.image.title="SentryView Frontend" \
      org.opencontainers.image.description="React frontend for SentryView RTSP NVR" \
      org.opencontainers.image.vendor="JorahOne" \
      org.opencontainers.image.version="2.1.0"

CMD ["nginx", "-g", "daemon off;"]
