import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from 'file:///C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import {finalizePresentation} from 'file:///C:/Users/benja/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root='C:/Users/benja/Desktop/Nueva carpeta (3)/sistema';
const dir=root+'/_guias/crud_biblioteca';
const skill='C:/Users/benja/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';

const originalLink=fs.link; fs.link=async (source,target)=>{try{return await originalLink(source,target)}catch(e){if(e.code!=='EPERM')throw e;return fs.copyFile(source,target,1)}};
const result=await finalizePresentation({workspaceDir:root,candidatePath:dir+'/build/draft.pptx',finalPath:dir+'/entrega/CRUD_biblioteca_paso_a_paso.pptx',pythonExecutable:'C:/Users/benja/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial','Consolas']},verifyArtifactToolImport:true,receiptPath:dir+'/build/validation.json'});console.log(JSON.stringify(result));


