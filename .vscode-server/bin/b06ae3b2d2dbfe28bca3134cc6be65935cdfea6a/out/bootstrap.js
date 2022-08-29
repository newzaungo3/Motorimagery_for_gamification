"use strict";(function(c,a){typeof exports=="object"?module.exports=a():c.MonacoBootstrap=a()})(this,function(){const c=typeof require=="function"?require("module"):void 0,a=typeof require=="function"?require("path"):void 0,f=typeof require=="function"?require("fs"):void 0;Error.stackTraceLimit=100,typeof process!="undefined"&&!process.env.VSCODE_HANDLES_SIGPIPE&&process.on("SIGPIPE",()=>{console.error(new Error("Unexpected SIGPIPE"))});function A(e){if(!a||!c||typeof process=="undefined"){console.warn("enableASARSupport() is only available in node.js environments");return}const n=e?a.join(e,"node_modules"):a.join(__dirname,"../node_modules");let r;if(e&&process.platform==="win32"){const t=e.substr(0,1);let i;t.toLowerCase()!==t?i=t.toLowerCase():i=t.toUpperCase(),r=i+n.substr(1)}else r=void 0;const s=`${n}.asar`,S=r?`${r}.asar`:void 0,u=c._resolveLookupPaths;c._resolveLookupPaths=function(t,i){const o=u(t,i);if(Array.isArray(o)){let d=!1;for(let l=0,P=o.length;l<P;l++)if(o[l]===n){d=!0,o.splice(l,0,s);break}else if(o[l]===r){d=!0,o.splice(l,0,S);break}!d&&e&&o.push(s)}return o}}function L(e,n){let r=e.replace(/\\/g,"/");r.length>0&&r.charAt(0)!=="/"&&(r=`/${r}`);let s;return n.isWindows&&r.startsWith("//")?s=encodeURI(`${n.scheme||"file"}:${r}`):s=encodeURI(`${n.scheme||"file"}://${n.fallbackAuthority||""}${r}`),s.replace(/#/g,"%23")}function N(){const e=h();let n={availableLanguages:{}};if(e&&e.env.VSCODE_NLS_CONFIG)try{n=JSON.parse(e.env.VSCODE_NLS_CONFIG)}catch{}if(n._resolvedLanguagePackCoreLocation){const r=Object.create(null);n.loadBundle=function(s,S,u){const t=r[s];if(t){u(void 0,t);return}v(n._resolvedLanguagePackCoreLocation,`${s.replace(/\//g,"!")}.nls.json`).then(function(i){const o=JSON.parse(i);r[s]=o,u(void 0,o)}).catch(i=>{try{n._corruptedFile&&E(n._corruptedFile,"corrupted").catch(function(o){console.error(o)})}finally{u(i,void 0)}})}}return n}function p(){return(typeof self=="object"?self:typeof global=="object"?global:{}).vscode}function h(){const e=p();if(e)return e.process;if(typeof process!="undefined")return process}function _(){const e=p();if(e)return e.ipcRenderer}async function v(...e){const n=_();if(n)return n.invoke("vscode:readNlsFile",...e);if(f&&a)return(await f.promises.readFile(a.join(...e))).toString();throw new Error("Unsupported operation (read NLS files)")}function E(e,n){const r=_();if(r)return r.invoke("vscode:writeNlsFile",e,n);if(f)return f.promises.writeFile(e,n);throw new Error("Unsupported operation (write NLS files)")}function b(){if(typeof process=="undefined"){console.warn("avoidMonkeyPatchFromAppInsights() is only available in node.js environments");return}process.env.APPLICATION_INSIGHTS_NO_DIAGNOSTIC_CHANNEL=!0,global.diagnosticsSource={}}return{enableASARSupport:A,avoidMonkeyPatchFromAppInsights:b,setupNLS:N,fileUriFromPath:L}});

//# sourceMappingURL=https://ticino.blob.core.windows.net/sourcemaps/b06ae3b2d2dbfe28bca3134cc6be65935cdfea6a/core/bootstrap.js.map