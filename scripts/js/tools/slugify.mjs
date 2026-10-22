// CLI entry point for the slugify helper.
process.argv.splice(2, 0, 'slugify');
await import('../toolbox.mjs');

