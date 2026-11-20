# Exec Summary — PR-2

- **Plan ID**: 8bb62ead
- **PR ID**: pr-2
- **Title**: Add client `upload_file` capability + protocol + orchestrator dispatch + transport FormData support
- **Branch**: `execute-plan/8bb62ead-pr-2` (linearized stack, also on `execute-plan/8bb62ead-pr-3` and `execute-plan/8bb62ead-final`)
- **Commit**: `a696cc9ca6513f0284963f2abfae71d103584ff9`
- **Status**: Done

## What changed

### Shared taxonomy (`packages/shared/src/client/`)
- `taxonomy_client_constant.ts`: added `export const ROUTE_UPLOAD = "/upload" as const;`.
- `taxonomy_client_vo.ts`: added `"upload_file"` to `ClientOperationVO`; added `readonly file?: File` to `ClientExecuteInput`; added `readonly uploadPath?: ClientUploadPathVO` to `ClientExecuteOutput`; added `ClientUploadPathVO { readonly value: string; }`.
- `taxonomy_client_response.ts`: added `UploadFileResponsePayload { readonly path: string; }`.
- `contract_client_protocol.ts`: added `IClientUploadProtocol { uploadFile(file: File, signal?: AbortSignal): Promise<UploadFileResponsePayload>; }`.
- `contract_client_aggregate.ts`: added `uploadFile` to `IClientAggregate`.
- `index.ts`: added barrel exports for the new types.

### Client capability (`packages/client/src/`)
- `capabilities_client_upload.ts` (NEW): `ClientUpload` class, 3-block capability structure (module declaration, contract class, helpers). Validates `.psd` extension (throws `ClientError` `INVALID_INPUT`). Builds `FormData`, calls `transport.post<UploadFileResponsePayload, FormData>(ROUTE_UPLOAD, form, signal)`.
- `capabilities_client_transport.ts`: `request()` detects `body instanceof FormData`, omits `Content-Type` for FormData (browser sets multipart boundary), passes body through.
- `agent_client_orchestrator.ts`: added `IClientUploadProtocol` import, `upload` dep, `uploadCapability` instance, `"upload_file"` case → `doUploadFile` (returns `{operation: "upload_file", uploadPath: {value: payload.path}}` or sentinel `{value: ""}` if no file), `uploadFile(file, signal?)` convenience wrapper.
- `root_client_container.ts`: added `ClientUpload` import + `const upload = new ClientUpload({transport})`, passed to `new ClientOrchestrator({inspect, render, stream, system, upload})`.

### Tests
- `packages/client/tests/unit_client_upload.test.ts` (NEW, 7 tests): valid upload, missing file, non-PSD extension, FormData construction, transport Content-Type omission, uploadPath VO, convenience wrapper.
- `packages/client/tests/contract_client_protocol.test.ts` (updated): protocol conformance for `IClientUploadProtocol`.
- `packages/client/tests/contract_client_conformance.test.ts`, `unit_client_orchestrator.test.ts`, `contract_client_schema.test.ts` (updated): upload mocks/assertions; `ROUTE_UPLOAD` added to `ALL_CLIENT_ROUTES`.

## Verification

- `npx vitest run --config root_config_vite_entry.ts` — full suite green (486 tests, 62 files).
- `npx tsc -p root_tsconfig_entry.json --noEmit` — no new errors vs. PR-1 baseline (the 6 errors reported earlier in this session were all in PR-3 test files, now fixed).
- `uv run ruff check modules/` — unchanged (PR-2 is TypeScript only).

## Notes

- Mirrors `packages/client/` patterns exactly: 3-block capability structure, orchestrator/container split, test-prefix convention.
- `ClientTransport.post()` FormData branch is the only transport change; all other methods are untouched.
- Studio surfaces stay passive — this PR only adds the client-side upload capability.