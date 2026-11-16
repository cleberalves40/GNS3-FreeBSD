--- gns3server/api/server.py.orig
+++ gns3server/api/server.py
@@ -21,0 +22,2 @@
+from contextlib import asynccontextmanager
+
@@ -57,0 +60,8 @@
+    @asynccontextmanager
+    async def lifespan(application):
+        await tasks.create_startup_handler(application)()
+        try:
+            yield
+        finally:
+            await tasks.create_shutdown_handler(application)()
+
@@ -63 +73,2 @@
-        redoc_url=None
+        redoc_url=None,
+        lifespan=lifespan,
@@ -74,2 +84,0 @@
-    application.add_event_handler("startup", tasks.create_startup_handler(application))
-    application.add_event_handler("shutdown", tasks.create_shutdown_handler(application))
