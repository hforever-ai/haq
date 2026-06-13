module.exports = {
  apps: [{
    name: "haq-bot",
    script: "dist/bot.js",
    interpreter: "node",
    cwd: "/opt/aarambha-haq/bots",
    env_file: "/opt/aarambha-haq/bots/.env",
    restart_delay: 5000,
    max_restarts: 10,
    watch: false,
  }]
};
