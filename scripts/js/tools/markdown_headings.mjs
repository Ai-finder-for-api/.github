// CLI entry point for the markdown-headings helper.
process.argv.splice(2, 0, 'markdown-headings');
await import('../toolbox.mjs');

