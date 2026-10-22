# 当前 local develop 与仍明示批准5f的两writer原差异

普通Git只读取得；不是新develop批准依据。两端path/bytes/SHA/blob见baseline-comparison。pyproject/lock两端逐字相同。

```diff
diff --git a/packages/engine/entrypoint.py b/packages/engine/entrypoint.py
index f5e9256..fef0e47 100644
--- a/packages/engine/entrypoint.py
+++ b/packages/engine/entrypoint.py
@@ -2,25 +2,13 @@

 import sys

+from ontolearn_engine.__main__ import main
+
 if __name__ == "__main__":
     if sys.argv[1:2] == ["--storage-probe"]:
         from ontolearn_engine.storage_probe import main as probe_main

         sys.argv.pop(1)
         probe_main()
-    elif sys.argv[1:2] == ["--worker"]:
-        from ontolearn_engine.worker import main as worker_main
-
-        worker_main()
-    elif sys.argv[1:2] == ["--contract-probe"]:
-        from ontolearn_engine.contract_probe import main as contract_probe_main
-
-        contract_probe_main()
-    elif sys.argv[1:2] == ["--protocol-resources"]:
-        from ontolearn_engine.resources import main as resource_main
-
-        resource_main()
     else:
-        from ontolearn_engine.__main__ import main
-
         main()
diff --git a/scripts/build-engine.mjs b/scripts/build-engine.mjs
index fb721d6..3044705 100644
--- a/scripts/build-engine.mjs
+++ b/scripts/build-engine.mjs
@@ -19,12 +19,6 @@ const result = spawnSync(
     'rdflib',
     '--copy-metadata',
     'pyparsing',
-    '--add-data',
-    `${resolve(root, 'packages/contracts/python/contract_v2.py')}:contracts/python`,
-    '--add-data',
-    `${resolve(root, 'packages/contracts/v2')}:contracts/v2`,
-    '--add-data',
-    `${resolve(root, 'uv.lock')}:provenance`,
     '--name',
     'ontolearn-engine',
     '--distpath',
@@ -35,12 +29,7 @@ const result = spawnSync(
     'build',
     'packages/engine/entrypoint.py',
   ],
-  {
-    cwd: root,
-    stdio: 'inherit',
-    shell: false,
-    env: { ...process.env, PYINSTALLER_CONFIG_DIR: resolve(root, 'build/pyinstaller-cache') },
-  },
+  { cwd: root, stdio: 'inherit', shell: false },
 )
 if (result.error) {
   console.error('需要先安装 uv 并执行 uv sync --frozen。')
```
