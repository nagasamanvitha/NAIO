/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Reduce bundle size
  swcMinify: true,
  // Faster page loads
  compress: true,
  // Optimize images
  images: {
    unoptimized: true, // For faster dev builds
  },
  // Reduce initial load time
  poweredByHeader: false,
}

module.exports = nextConfig
