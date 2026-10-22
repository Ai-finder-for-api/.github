// CLI entry point for the safe-filename helper.
process.argv.splice(2, 0, 'safe-filename');
await import('../toolbox.mjs');

