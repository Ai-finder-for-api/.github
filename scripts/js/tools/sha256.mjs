// CLI entry point for the sha256 helper.
process.argv.splice(2, 0, 'sha256');
await import('../toolbox.mjs');

