import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
const command = process.argv[2], args = process.argv.slice(3), input = args[0];
const read = async (p=input) => readFile(p,"utf8");
const slugify = s => s.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");
const safeFilename = s => s.replace(/[<>:"/\\|?*\x00-\x1f]/g,"-").replace(/[. ]+$/g,"").trim() || "untitled";
async function tree(dir){let out=[];for(const e of await readdir(dir,{withFileTypes:true})){if([".git","node_modules",".venv","venv","__pycache__"].includes(e.name))continue;const p=path.join(dir,e.name);out.push((e.isDirectory()?"DIR ":"FILE ")+p);if(e.isDirectory())out.push(...await tree(p));}return out;}
function headings(s){return [...s.matchAll(/^(#{1,6})\s+(.+)$/gm)].map(m=>({level:m[1].length,text:m[2].trim(),slug:slugify(m[2].trim())}));}
function parseCsv(s){const rows=[];let row=[],field="",quoted=false;for(let i=0;i<s.length;i++){const c=s[i];if(quoted){if(c==='"'&&s[i+1]==='"'){field+='"';i++;}else if(c==='"')quoted=false;else field+=c;}else if(c==='"')quoted=true;else if(c===","){row.push(field);field="";}else if(c==="\n"){row.push(field);rows.push(row);row=[];field="";}else if(c!=="\r")field+=c;}if(field.length||row.length){row.push(field);rows.push(row);}return rows;}
function toCsv(rows){return rows.map(r=>r.map(v=>{const s=String(v??"");return /[",\r\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;}).join(",")).join("\n")+"\n";}
async function mediaManifest(dir){const exts=new Set([".png",".jpg",".jpeg",".webp",".gif",".mp4",".webm",".svg",".mp3",".wav",".ogg"]);let out=[];for(const p of await tree(dir)){if(!p.startsWith("FILE "))continue;const file=p.slice(5);if(exts.has(path.extname(file).toLowerCase()))out.push({path:file,bytes:(await stat(file)).size});}return out;}
let out;
switch(command){
case "slugify": out=slugify(args.join(" ")); break;
case "safe-filename": out=safeFilename(args.join(" ")); break;
case "word-count": {const s=await read();out={words:(s.match(/\b[\p{L}\p{N}_'-]+\b/gu)||[]).length,characters:s.length,lines:s.split(/\r?\n/).length};break;}
case "json-format": out=JSON.stringify(JSON.parse(await read()),null,2);break;
case "json-sort": {const sort=v=>Array.isArray(v)?v.map(sort):v&&typeof v==="object"?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sort(v[k])])):v;out=JSON.stringify(sort(JSON.parse(await read())),null,2);break;}
case "json-minify": out=JSON.stringify(JSON.parse(await read()));break;
case "json-to-csv": {const d=JSON.parse(await read());const rows=Array.isArray(d)?d:[d];const keys=[...new Set(rows.flatMap(o=>Object.keys(o)))];out=toCsv([keys,...rows.map(o=>keys.map(k=>o[k]))]);break;}
case "csv-to-json": {const rows=parseCsv(await read());const [head,...body]=rows;out=JSON.stringify(body.map(r=>Object.fromEntries(head.map((k,i)=>[k,r[i]??""]))),null,2);break;}
case "sha256": out=crypto.createHash("sha256").update(await readFile(input)).digest("hex");break;
case "text-stats": {const s=await read();out={characters:s.length,lines:s.split(/\r?\n/).length,words:(s.match(/\b[\p{L}\p{N}_'-]+\b/gu)||[]).length};break;}
case "markdown-toc": out=headings(await read()).map(h=>Array(h.level).join("  ")+"- ["+h.text+"](#"+h.slug+")").join("\n");break;
case "markdown-headings": out=headings(await read());break;
case "normalize-newlines": out=(await read()).replace(/\r\n?/g,"\n");break;
case "trailing-whitespace": {const s=await read();out=s.split(/\r?\n/).map((v,i)=>({line:i+1,hasTrailingWhitespace:/[ \t]+$/.test(v)})).filter(x=>x.hasTrailingWhitespace);break;}
case "timestamp": out=new Date(args[0]??Date.now()).toISOString();break;
case "duration": {let n=Math.max(0,Math.floor(Number(input)));out=Math.floor(n/86400)+"d "+Math.floor(n%86400/3600)+"h "+Math.floor(n%3600/60)+"m "+(n%60)+"s";break;}
case "hex-rgb": {let h=input.replace(/^#/,"");if(h.length===3)h=[...h].map(c=>c+c).join("");if(!/^[0-9a-f]{6}$/i.test(h))throw Error("Use #RGB or #RRGGBB");out={r:parseInt(h.slice(0,2),16),g:parseInt(h.slice(2,4),16),b:parseInt(h.slice(4,6),16)};break;}
case "relative-path": out=path.relative(args[0]||".",args[1]||".");break;
case "repo-tree": out=(await tree(input||".")).join("\n");break;
case "media-manifest": out=await mediaManifest(input||".");break;
case "line-count": out=(await read()).split(/\r?\n/).length;break;
case "dedupe-lines": out=[...new Set((await read()).split(/\r?\n/))].join("\n");break;
case "sort-lines": out=(await read()).split(/\r?\n/).sort((a,b)=>a.localeCompare(b)).join("\n");break;
case "csv-summary": {const rows=parseCsv(await read());out={rows:Math.max(0,rows.length-1),columns:rows[0]?.length??0,headers:rows[0]??[]};break;}
case "validate-json": {JSON.parse(await read());out={valid:true,file:input};break;}
case "list-extensions": {const files=(await tree(input||".")).filter(s=>s.startsWith("FILE ")).map(s=>path.extname(s.slice(5)).toLowerCase()||"[no extension]");out=Object.fromEntries([...new Set(files)].sort().map(ext=>[ext,files.filter(x=>x===ext).length]));break;}
case "merge-json": {const a=JSON.parse(await read(args[0])),b=JSON.parse(await read(args[1]));if(!a||!b||Array.isArray(a)||Array.isArray(b)||typeof a!=="object"||typeof b!=="object")throw Error("Both files must contain JSON objects");out=JSON.stringify({...a,...b},null,2);break;}
case "diff-json": {const a=JSON.parse(await read(args[0])),b=JSON.parse(await read(args[1]));const keys=[...new Set([...Object.keys(a),...Object.keys(b)])];out=keys.filter(k=>JSON.stringify(a[k])!==JSON.stringify(b[k])).map(k=>({key:k,before:a[k]??null,after:b[k]??null}));break;}
case "env-names": out=Object.keys(process.env).filter(k=>/(token|key|secret|password|auth)/i.test(k)).sort();break;
case "log-summary": {const lines=(await read()).split(/\r?\n/);out={lines:lines.length,errors:lines.filter(x=>/error|fatal/i.test(x)).length,warnings:lines.filter(x=>/warn/i.test(x)).length};break;}
default: console.error("Unknown toolbox command:",command);process.exit(2);
}
console.log(typeof out==="string"?out:JSON.stringify(out,null,2));
