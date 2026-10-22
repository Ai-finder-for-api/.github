// CLI entry point for the list-extensions helper.
process.argv.splice(2, 0, 'list-extensions');
await import('../toolbox.mjs');

