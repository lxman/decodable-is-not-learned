from pathlib import Path
import importlib
import importlib.util
import os
import sys
import unittest
import _thread
from exp7core.contract import Refusal
from exp7core.records import strict_json
from exp7stats.common import digest, dumps
from exp7stats.candidate_audit import code_hash
import test_integration_boundaries as ib


class SourceClosureTests(unittest.TestCase):
    def candidate(self):
        helper=ib.IntegrationBoundaryTests();helper.setUp();self.addCleanup(helper.doCleanups)
        return helper.candidate()

    def bind(self, ctx, content, runtime):
        content["runtime.json"]=dumps(runtime)
        (ctx.repo/"runtime.json").write_bytes(content["runtime.json"])
        manifest=strict_json(content["manifest.json"])
        manifest["files"]["runtime.json"]["sha256"]=digest(content["runtime.json"])
        content["manifest.json"]=dumps(manifest)
        (ctx.repo/"manifest.json").write_bytes(content["manifest.json"])
        ctx.manifest_sha=digest(content["manifest.json"])

    def test_SR1_exact_external_helper_allowance_and_aliases_work(self):
        ctx,content=self.candidate()
        path=ctx.repo.parent/"external.py";path.write_text("MARKER = 'EXACT-BOUND'\n")
        runtime=strict_json(content["runtime.json"])
        runtime["files"][str(path.resolve())]={"role":"helper","sha256":digest(path.read_bytes())}
        self.bind(ctx,content,runtime)
        with ctx.entryexit("calibration"):
            for name in ("sr_external_alias_a","sr_external_alias_b"):
                spec=importlib.util.spec_from_file_location(name,path)
                module=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.assertEqual(module.MARKER,"EXACT-BOUND")

    def test_SR1_unbound_generated_exec_and_filename_spoof_refuse(self):
        for filename in ("<sr-unbound-generated>", "candidate.py"):
            ctx,content=self.candidate()
            filename=str(ctx.repo/filename) if filename.endswith(".py") else filename
            code=compile("MARKER = 'UNBOUND'",filename,"exec")
            with self.assertRaisesRegex(Refusal,"unbound generated/altered"):
                with ctx.entryexit("calibration"):
                    exec(code,{})

    def test_SR1_exact_generated_code_requires_independent_fingerprint(self):
        ctx,content=self.candidate()
        code=compile("MARKER = 'BOUND'","<sr-approved-generated>","exec")
        runtime=strict_json(content["runtime.json"])
        path=str((ctx.repo/"candidate.py").resolve())
        runtime["generated"][code_hash(code)]={"producer":path,"producer_sha256":digest(content["candidate.py"])}
        self.bind(ctx,content,runtime)
        with ctx.entryexit("calibration"):
            result={};exec(code,result)
            self.assertEqual(result["MARKER"],"BOUND")

    def test_SR1_precompiled_function_outside_without_exec_event_refuses(self):
        ctx,_=self.candidate()
        namespace={}
        exec(compile("def run():\n    return 'BAD'\n",str(ctx.repo.parent/"unbound.py"),"exec"),namespace)
        with self.assertRaisesRegex(Refusal,"unpinned external"):
            with ctx.entryexit("calibration"):
                namespace["run"]()

    def test_SR3_existing_and_dangling_bytecode_refuse(self):
        for symlink in (False,True):
            ctx,_=self.candidate()
            cache=Path(importlib.util.cache_from_source(str(ctx.repo/"helper.py")))
            cache.parent.mkdir()
            if symlink:cache.symlink_to(ctx.repo/"missing-pyc")
            else:cache.write_bytes(b"forbidden-existing-bytecode")
            with self.assertRaises(Refusal):
                with ctx.entryexit("calibration"):
                    cache.read_bytes()

    def test_SR3_absent_cache_probe_cannot_race_into_successful_read(self):
        ctx,_=self.candidate()
        cache=Path(importlib.util.cache_from_source(str(ctx.repo/"helper.py")))
        cache.parent.mkdir()
        original=Path.lstat
        def racing_lstat(path,*args,**kwargs):
            if path == cache:
                cache.write_bytes(b"racing-unbound-bytecode")
                raise FileNotFoundError(str(cache))
            return original(path,*args,**kwargs)
        try:
            with ctx.entryexit("calibration"):
                Path.lstat=racing_lstat
                try:
                    with self.assertRaises(FileNotFoundError):cache.read_bytes()
                finally:
                    Path.lstat=original
                    cache.unlink()
        finally:
            Path.lstat=original

    def test_SR1_serial_guard_refuses_untraced_thread_before_start(self):
        ctx,_=self.candidate()
        with self.assertRaisesRegex(Refusal,"untraced Python threads"):
            with ctx.entryexit("calibration"):
                _thread.start_new_thread(lambda:None,())
