// CLI entry point for the markdown-toc helper.
process.argv.splice(2, 0, 'markdown-toc');
await import('../toolbox.mjs');

