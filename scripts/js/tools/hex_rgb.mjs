// CLI entry point for the hex-rgb helper.
process.argv.splice(2, 0, 'hex-rgb');
await import('../toolbox.mjs');

