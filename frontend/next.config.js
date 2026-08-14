/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['coin-images.coingecko.com', 'localhost'],
  },
  trailingSlash: false,
  experimental: {
    appDir: true,
  },
};

module.exports = nextConfig;