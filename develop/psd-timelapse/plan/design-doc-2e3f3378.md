# Technical Design Document: Redesign Client Package as a Feature Folder with Business Logic

**Document ID:** `design-doc-2e3f3378`  
**Status:** DRAFT / PROPOSED  
**Author:** GrokBuild Systems Architect  
**Date:** 2026-11-18  
**Target Workspace:** `psd-timelapse` (`packages/` web workspace)  

---

## 1. Executive Summary & Objective

This document specifies the architectural redesign of the Web UI HTTP client within the `psd-timelapse` repository. In the current system, the web presentation layer (`packages/home`, `packages/studio`, `packages/queue`, `packages/gallery`, `packages/shell`) relies on static mock fixtures and stubs because the legacy client/orchestrator package was removed (`packages/root_web_container.ts`).

The objective is to introduce a robust, fully compliant Agentic Engineering System (AES) **feature folder** named `client/` that encapsulates all client-side business logic, API communication, and state orchestration needed to drive the local Python FastAPI backend (`modules/api/`).

Under the strict tenets of AES vertical slicing and separation of concerns:
1. `client/` is designed as a **feature folder** containing business logic, not as a surface presentation layer.
2. The implementation is cleanly bifurcated across two specific locations:
   - `packages/shared/src/client/`: Holds domain foundation taxonomy (value objects, request/response models, error classes, constants), contract definitions (subsystem protocols and aggregate interface), and stateless low-level utility functions.
   - `packages/client/src/`: Holds concrete capability implementations (`capabilities_client_<namafeature>`) and the agent orchestrator (`agent_client_orchestrator`), alongside its composition root (`root_client_container.ts`).
3. The surface layer (pages, views, components, layouts, hooks, stores) **never** communicates with the Python API directly, nor does it import concrete capabilities. All interaction with the backend flows through the client feature's contract aggregate (`IClientAggregate`).
4. Complete functional specifications (`FRD.md`) and tracking manifests (`BACKLOG.md`) are established for both the feature package and its shared domain counterpart.

---

## 2. Problem Statement & Motivation

### 2.1 Current State
In the current web package topology:
- `packages/root_web_container.ts` contains a stubbed `createWebDependencies()` returning `null` values for `apiClient`, `errorHandler`, `orchestrator`, `tenantProtocol`, and `tenantAggregate`.
- `packages/studio/`, `packages/queue/`, `packages/gallery/`, and `packages/home/` use hardcoded mock fixtures (`DEMO_ACTIVE`, `DEMO_QUEUED`, `DEMO_COMPLETED`, etc.) embedded directly in surface files.
- The Python backend in `modules/api/` exposes production-ready endpoints (`/api/health`, `/api/config`, `/api/inspect`, `/api/renders`, `/api/renders/{run_id}`, `/api/renders/{run_id}/progress`, `/api/renders/{run_id}/events`, `/api/renders/{run_id}/cancel`, `/api/renders/{run_id}/retry`, `/api/renders/{run_id}/view`, `/api/renders/{run_id}/output`, and `/api/renders/{run_id}/output/meta`), but no frontend module interfaces with them.

### 2.2 Architectural Risks of Ad-Hoc Fetching
Allowing surface components or React hooks to invoke `fetch()` directly creates severe architectural anti-patterns:
- **AES406 & AES201 Violations:** Passive surfaces (`surface_*_component.tsx`, `surface_*_view.tsx`, `surface_*_layout.tsx`) must never perform networking, I/O, or state machine transitions.
- **Scattered Domain Logic:** Polling timers, SSE reconnection logic, error normalization, and inspection caching would become duplicated across multiple UI panels.
- **Tight Coupling:** Any change to backend route paths or serialization formats would cascade into UI templates.

### 2.3 Proposed Solution: Client as a Feature Folder
By classifying `client/` as a **feature folder** (governed by AES702 and AES403/AES405):
- External API mechanics are isolated in cohesive **Capabilities** (`capabilities_client_*`).
- High-level business choreography (polling vs. SSE fallback, request sequencing, lifecycle tracking) is coordinated by an **Agent Orchestrator** (`agent_client_orchestrator`).
- Clean contracts (`contract_client_aggregate.ts` and `contract_client_protocol.ts`) decouple UI presentation from network protocols and wire formats.

---

## 3. Architectural Topology & Import Boundaries

### 3.1 Two-Location Split

The architecture divides the client concern into two dedicated paths:

```text
packages/
├── shared/
│   ├── BACKLOG.md
│   ├── DATA.md
│   └── src/
│       ├── common/
│       │   └── styles.css
│       ├── utility_shared_cta.ts
│       └── client/                             <-- LOCATION 1: Shared Domain & Contracts
│           ├── BACKLOG.md
│           ├── DATA.md
│           ├── contract_client_aggregate.ts    # IClientAggregate (consumed by Surface)
│           ├── contract_client_protocol.ts     # Subsystem protocols (implemented by Capabilities)
│           ├── taxonomy_client_constant.ts     # Client configuration constants & route paths
│           ├── taxonomy_client_error.ts        # ClientError, ApiTransportError, NetworkConnectionError, ServerStreamError
│           ├── taxonomy_client_request.ts      # Wire request interfaces
│           ├── taxonomy_client_response.ts     # Wire response interfaces
│           ├── taxonomy_client_vo.ts           # Domain value objects (RunIdVO, LayerMetadataVO, PsdDocumentInfoVO, ProgressSnapshotVO, RenderOutputMetaVO, SystemConfigVO, SystemHealthVO)
│           ├── utility_client_parser.ts        # Stateless SSE & JSON payload parser
│           └── utility_client_url.ts           # Stateless URL/query builder
└── client/                                     <-- LOCATION 2: Feature Folder (Business Logic)
    ├── BACKLOG.md
    ├── FRD.md
    ├── src/
    │   ├── index.ts                            # Public entrypoint for package consumers
    │   ├── agent_client_orchestrator.ts        # Coordinates capabilities, implements IClientAggregate
    │   ├── capabilities_client_inspect.ts      # PSD inspection logic & layer classification adapter
    │   ├── capabilities_client_render.ts       # Render job lifecycle (start, cancel, retry, result)
    │   ├── capabilities_client_stream.ts       # SSE event stream subscriber & event demuxer
    │   ├── capabilities_client_system.ts       # Health checks & configuration retrieval
    │   ├── capabilities_client_transport.ts    # Low-level HTTP transport over fetch & error envelope parsing
    │   └── root_client_container.ts            # DI container wiring capabilities into orchestrator
    └── tests/
        ├── contract_client_conformance.test.ts # Protocol conformance validation
        ├── integration_client_flow.test.ts     # Multi-capability lifecycle tests
        ├── unit_client_inspect.test.ts         # Inspection capability unit tests
        ├── unit_client_orchestrator.test.ts    # Agent orchestrator unit tests
        ├── unit_client_render.test.ts          # Render capability unit tests
        ├── unit_client_stream.test.ts          # SSE stream capability unit tests
        ├── unit_client_system.test.ts          # Health/config capability unit tests
        └── unit_client_transport.test.ts       # HTTP transport unit tests
```

### 3.2 AES Import Matrix Enforcement

The implementation adheres to the AES Group 2 Import Matrix:

| Consumer Layer | Permitted Inbound Imports | Prohibited Inbound Imports |
|---|---|---|
| **Taxonomy** (`taxonomy_client_*`) | Taxonomy | Contract, Capabilities, Agent, Surface, Utility, Root |
| **Utility** (`utility_client_*`) | Taxonomy | Contract, Capabilities, Agent, Surface, Utility, Root |
| **Contract (Protocol)** (`contract_client_protocol.ts`) | Taxonomy, Contract | Capabilities, Agent, Surface, Root, Contract (Aggregate) |
| **Contract (Aggregate)** (`contract_client_aggregate.ts`) | Taxonomy, Contract | Capabilities, Agent, Surface, Root |
| **Capabilities** (`capabilities_client_*`) | Taxonomy, Contract (Protocol), Utility | Other Capabilities, Agent, Surface, Root, Contract (Aggregate) |
| **Agent** (`agent_client_orchestrator.ts`) | Taxonomy, Contract (Aggregate), Contract (Protocol), Utility | Concrete Capabilities, Surface, Root |
| **Surface** (`packages/*/src/surface_*`) | Taxonomy, Contract (Aggregate), Utility | Concrete Capabilities, Contract (Protocol), Agent, Root |
| **Root** (`root_client_container.ts`, `root_web_container.ts`) | Taxonomy, Contract, Capabilities, Agent, Surface | None |

---

## 4. Shared Layer Specifications (`packages/shared/src/client/`)

The shared client directory provides the contracts, taxonomy value objects, and stateless utility mechanics that define the interface between frontend consumers and the client feature.

### 4.1 Taxonomy Layer

#### `taxonomy_client_constant.ts`
Defines compile-time constant values and API route templates:
- `API_BASE_URL_DEFAULT = "http://127.0.0.1:8000/api"`
- Route endpoints:
  - `ROUTE_HEALTH = "/health"`
  - `ROUTE_CONFIG = "/config"`
  - `ROUTE_INSPECT = "/inspect"`
  - `ROUTE_RENDERS = "/renders"`
  - `ROUTE_RENDER_DETAIL = "/renders/:run_id"`
  - `ROUTE_RENDER_PROGRESS = "/renders/:run_id/progress"`
  - `ROUTE_RENDER_CANCEL = "/renders/:run_id/cancel"`
  - `ROUTE_RENDER_RETRY = "/renders/:run_id/retry"`
  - `ROUTE_RENDER_EVENTS = "/renders/:run_id/events"`
  - `ROUTE_RENDER_VIEW = "/renders/:run_id/view"`
  - `ROUTE_OUTPUT = "/renders/:run_id/output"`
  - `ROUTE_OUTPUT_META = "/renders/:run_id/output/meta"`
- Tuning parameters:
  - `POLL_INTERVAL_DEFAULT_MS = 250`
  - `TIMEOUT_DEFAULT_MS = 10000`
  - `SSE_RECONNECT_INTERVAL_MS = 1000` — fallback reconnect interval used by `ClientStreamCapability` **only** until the backend's opening `retry: <ms>` frame is parsed; once received, the server-provided value supersedes this default (see §5.1 Capability 4). Retained because the chunked-`fetch` reader (chosen over `EventSource`) has no built-in backoff and must own reconnect timing itself.

#### `taxonomy_client_vo.ts`
Defines domain Value Objects and readonly data models:
```typescript
export interface RunIdVO {
  readonly value: string;
}

export type PipelineStageVO =
  | "idle"
  | "validating"
  | "planning"
  | "animating"
  | "compositing"
  | "encoding"
  | "completed"
  | "failed"
  | "cancelled";
// Source of truth: modules/shared/src/common/taxonomy_pipeline_state_vo.py
// `PipelineStage(StrEnum)`. The union must match the live StrEnum values
// verbatim — no `"scripting"`, no `"rendering"` (the backend never emits
// those). Pinned by `contract_client_schema.test.ts` (see §8): the test
// reads the live `PipelineStage` members via the OpenAPI `ProgressResponse`
// schema and fails if this union drifts.

export type LayerClassificationType = string;

export interface LayerBoundsVO {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface LayerMetadataVO {
  readonly name: string;
  readonly classification: LayerClassificationType;
  readonly revealStyle: string;
  readonly visible: boolean;
  readonly bounds: LayerBoundsVO;
}

export interface PsdDocumentInfoVO {
  readonly valid: boolean;
  readonly summary: Record<string, unknown>;
  readonly layerCount: number;
  readonly layers: readonly LayerMetadataVO[];
}

export interface ProgressSnapshotVO {
  readonly runId: string;
  readonly stage: PipelineStageVO;
  readonly current: number;
  readonly total: number;
  readonly percent: number;
  readonly message: string;
}

export interface RenderOutputMetaVO {
  readonly available: boolean;
  readonly videoPath: string | null;
  readonly sizeBytes: number | null;
  readonly state: string;
}

export interface SystemConfigVO {
  readonly outputDir: string;
  readonly workspaceDir: string;
  readonly width: number;
  readonly height: number;
  readonly fps: number;
  readonly crf: number;
  readonly codec: string;
  readonly preset: string;
  readonly pixelFormat: string;
  readonly cleanupOnFailure: boolean;
}

export interface SystemHealthVO {
  readonly status: "ok" | "degraded" | "unavailable";
  readonly state: string;
}
```

#### `taxonomy_client_request.ts`
Encapsulates backend request payloads:
```typescript
export interface InspectInputRequest {
  readonly input_path: string;
}

export interface StartRenderRequest {
  readonly input_path: string;
  readonly output_path?: string | null;
}
```

#### `taxonomy_client_response.ts`
Matches the FastAPI schemas defined in `modules/api/src/surface_api_schema_view.py`:
```typescript
export interface HealthResponsePayload {
  readonly status: string;
  readonly state: string;
}

export interface ConfigResponsePayload {
  readonly output_dir: string;
  readonly workspace_dir: string;
  readonly width: number;
  readonly height: number;
  readonly fps: number;
  readonly crf: number;
  readonly codec: string;
  readonly preset: string;
  readonly pixel_format: string;
  readonly cleanup_on_failure: boolean;
}

export interface LayerPayload {
  readonly name: string;
  readonly classification: string;
  readonly reveal_style: string;
  readonly bounds: Record<string, number>;
  readonly visible: boolean;
}

export interface InspectResponsePayload {
  readonly valid: boolean;
  readonly summary: Record<string, unknown>;
  readonly layer_count: number;
  readonly layers: readonly LayerPayload[];
}

export interface RunHandleResponsePayload {
  readonly run_id: string;
  readonly state: string;
  readonly input_path: string;
}

export interface ProgressResponsePayload {
  readonly run_id: string;
  readonly stage: string;
  readonly current: number;
  readonly total: number;
  readonly percent: number;
  readonly message: string;
}

export interface RunErrorDetailPayload {
  readonly code: string;
  readonly message: string;
  readonly stage: string | null;
}

export interface RunResultResponsePayload {
  readonly run_id: string;
  readonly state: string;
  readonly input_path: string;
  readonly video_path: string | null;
  readonly scripting_manifest_path: string | null;
  readonly animator_manifest_path: string | null;
  readonly total_frames: number;
  readonly fps: number;
  readonly error: RunErrorDetailPayload | null;
}

export interface CancelResponsePayload {
  readonly cancelled: boolean;
}

export interface RunViewResponsePayload {
  readonly run_id: string;
  readonly stage: string;
  readonly progress: number;
  readonly output_path: string | null;
  readonly error: RunErrorDetailPayload | null;
}

export interface OutputMetaResponsePayload {
  readonly available: boolean;
  readonly video_path: string | null;
  readonly size_bytes: number | null;
  readonly state: string;
}

export interface ApiErrorEnvelopePayload {
  readonly error: {
    readonly code: string;
    readonly message: string;
    readonly stage?: string | null;
  };
}
```

#### `taxonomy_client_error.ts`
Defines error classifications and domain exceptions:
```typescript
export class ClientError extends Error {
  readonly code: string;
  readonly retryable: boolean;
  readonly status?: number;

  constructor(
    message: string,
    code = "CLIENT_ERROR",
    retryable = false,
    status?: number,
    cause?: unknown
  ) {
    // Forward `cause` to the standard ES2022 Error constructor so it surfaces in
    // stack traces / `util.inspect` and `instanceof Error` stays correct.
    super(message, cause !== undefined ? { cause } : undefined);
    this.name = "ClientError";
    this.code = code;
    this.retryable = retryable;
    this.status = status;
  }
}

export class ApiTransportError extends ClientError {
  readonly stage?: string;

  constructor(message: string, code: string, status: number, retryable = false, stage?: string) {
    super(message, code, retryable, status);
    this.name = "ApiTransportError";
    this.stage = stage;
  }
}

export class NetworkConnectionError extends ClientError {
  constructor(message: string, cause?: unknown) {
    super(message, "NETWORK_CONNECTION_ERROR", true, undefined, cause);
    this.name = "NetworkConnectionError";
  }
}

export class ServerStreamError extends ClientError {
  constructor(message: string) {
    super(message, "STREAM_ERROR", true);
    this.name = "ServerStreamError";
  }
}
```

---

### 4.2 Utility Layer

Stateless standalone helper functions (AES404 compliant — no classes, no state, no contracts).

#### `utility_client_url.ts`
- `buildApiUrl(baseUrl: string, endpointTemplate: string, params?: Record<string, string>): string` — Composes `baseUrl + formatRoute(endpointTemplate, params)`. The single entry point capabilities use to turn a `taxonomy_client_constant.ts` route template into a fully-qualified URL. If `params` is supplied it is forwarded to `formatRoute`; otherwise the template is appended verbatim.
- `formatRoute(template: string, replacements: Record<string, string>): string` — Substitutes `:placeholder` tokens in the template with values from `replacements`. The replacement **key matches the colon placeholder name exactly** (e.g. `ROUTE_RENDER_DETAIL = "/renders/:run_id"` requires key `"run_id"`, not `"runId"`). Each replacement value is passed through `encodeURIComponent` before substitution (run IDs are UUIDs so encoding is a no-op in practice, but the contract is explicit and protects against future identifiers that contain `/` or other reserved characters). Placeholders with no matching key are left in the template unchanged (an implementer bug; covered by a `formatRoute` unit test).
- `appendQueryParams(url: string, query: Record<string, string | number | boolean | undefined>): string` — Appends URL-encoded query-string parameters to a fully-built URL. Used **only** for GET query strings (e.g. a future `?limit=` on `/api/renders`). `undefined` values are dropped; others are URL-encoded via `URLSearchParams`. Does **not** touch path templates — that is `formatRoute`/`buildApiUrl`'s responsibility.
- **Responsibility boundary:** `buildApiUrl` = `baseUrl` + path template composition; `formatRoute` = path-template placeholder substitution (used by `buildApiUrl`); `appendQueryParams` = query-string assembly on a completed URL. A capability calls `buildApiUrl(baseUrl, ROUTE_RENDERS, { run_id })` and, only if it needs query parameters, chains `.pipe` through `appendQueryParams`. No overlap: path substitution never happens in `appendQueryParams`, and query assembly never happens in `buildApiUrl`.
- **Example:**
  ```typescript
  buildApiUrl("http://127.0.0.1:8000/api", "/renders/:run_id", { run_id: "abc-123" })
  // => "http://127.0.0.1:8000/api/renders/abc-123"
  appendQueryParams("http://127.0.0.1:8000/api/renders", { limit: 10, active: true })
  // => "http://127.0.0.1:8000/api/renders?limit=10&active=true"
  ```

#### `utility_client_parser.ts`
- `parseSseChunk(chunk: string): Array<{ event?: string; data: string; id?: string }>` — Splits a raw SSE chunk on blank-line boundaries and extracts typed `event:`, `data:`, and `id:` fields from each frame. Ignores `retry:` lines (handled upstream).
- `parseJsonSafely<T>(text: string, fallback: T): T`
- `normalizeErrorEnvelope(status: number, json: unknown): ApiTransportError` — Unwraps the backend's nested `{error:{code,message,stage?}}` envelope into an `ApiTransportError`. Derives `retryable` from HTTP status: 408/425/429/5xx → retryable; 400/404/422 → not retryable; 409 → retryable only for `ACTIVE_JOB_CONFLICT`.

---

### 4.3 Contract Layer

#### `contract_client_protocol.ts` (Subsystem Protocols)
Defines protocols implemented by individual capabilities:

```typescript
import type {
  InspectInputRequest,
  StartRenderRequest,
} from "./taxonomy_client_request";
import type {
  ConfigResponsePayload,
  HealthResponsePayload,
  InspectResponsePayload,
  OutputMetaResponsePayload,
  ProgressResponsePayload,
  RunHandleResponsePayload,
  RunResultResponsePayload,
  RunViewResponsePayload,
  CancelResponsePayload,
} from "./taxonomy_client_response";

/** Low-level HTTP transport protocol. */
export interface IClientTransportProtocol {
  get<T>(path: string, signal?: AbortSignal): Promise<T>;
  post<T, B = unknown>(path: string, body?: B, signal?: AbortSignal): Promise<T>;
}

/** PSD inspection capability protocol. */
export interface IClientInspectProtocol {
  inspectPsd(request: InspectInputRequest, signal?: AbortSignal): Promise<InspectResponsePayload>;
}

/** Render lifecycle capability protocol. */
export interface IClientRenderProtocol {
  startRender(request: StartRenderRequest, signal?: AbortSignal): Promise<RunHandleResponsePayload>;
  getProgress(runId: string, signal?: AbortSignal): Promise<ProgressResponsePayload>;
  getResult(runId: string, signal?: AbortSignal): Promise<RunResultResponsePayload>;
  getView(runId: string, signal?: AbortSignal): Promise<RunViewResponsePayload>;
  getOutputMeta(runId: string, signal?: AbortSignal): Promise<OutputMetaResponsePayload>;
  cancelRender(runId: string, signal?: AbortSignal): Promise<CancelResponsePayload>;
  retryRender(runId: string, signal?: AbortSignal): Promise<RunHandleResponsePayload>;
}

/** Server-Sent Events stream capability protocol. */
export interface IClientStreamProtocol {
  subscribeEvents(
    runId: string,
    onState: (state: { stage: string; run_id: string; terminal: boolean }) => void,
    onProgress: (progress: ProgressResponsePayload) => void,
    onTerminal: (result: RunResultResponsePayload) => void,
    onError: (error: Error) => void
  ): () => void;
}

/** System diagnostic and configuration protocol. */
export interface IClientSystemProtocol {
  getHealth(signal?: AbortSignal): Promise<HealthResponsePayload>;
  getConfig(signal?: AbortSignal): Promise<ConfigResponsePayload>;
}
```

#### `contract_client_aggregate.ts` (Aggregate Interface)
The singular public interface consumed by the presentation/surface layer:

```typescript
import type {
  PsdDocumentInfoVO,
  ProgressSnapshotVO,
  RenderOutputMetaVO,
  SystemConfigVO,
  SystemHealthVO,
} from "./taxonomy_client_vo";

export interface RenderExecutionHandle {
  readonly runId: string;
  readonly state: string;
  readonly inputPath: string;
}

export interface IClientAggregate {
  /** Inspect a PSD file at a given path. */
  inspect(inputPath: string, signal?: AbortSignal): Promise<PsdDocumentInfoVO>;

  /** Initiate an MP4 timelapse render job. */
  startRender(inputPath: string, outputPath?: string | null, signal?: AbortSignal): Promise<RenderExecutionHandle>;

  /** Query a single polled view of an active job — stage, monotonic percent, and
   *  output/error evidence — via `IClientRenderProtocol.getView`. The view is
   *  the polled-path counterpart to the streaming `watchProgress` path and
   *  replaces the prior `getProgress` mapping so the polled path names exactly
   *  one capability method (`getView` → `ROUTE_RENDER_VIEW`).
   *  `getProgress`/`ROUTE_RENDER_PROGRESS` remain defined on the render
   *  capability and unit-tested but are not wired into any `IClientAggregate`
   *  method; no surface or orchestrator consumer routes through them. */
  checkProgress(runId: string, signal?: AbortSignal): Promise<ProgressSnapshotVO>;

  /** Fetch final output evidence and metadata for a completed job via
   *  `IClientRenderProtocol.getOutputMeta` (`ROUTE_OUTPUT_META`). The richer
   *  `RunResultResponse` (`total_frames`, `fps`, manifests) that
   *  `IClientRenderProtocol.getResult` returns is a stream-only terminal
   *  payload delivered to `watchProgress.onComplete`; no aggregate method
   *  surfaces it. If a future caller needs the run's `total_frames`/`fps`/
   *  manifests, this method is the natural widening point (add fields to
   *  `RenderOutputMetaVO` or a sibling `fetchRunResult` method). */
  fetchResult(runId: string, signal?: AbortSignal): Promise<RenderOutputMetaVO>;

  /** Cancel an active render job. */
  cancel(runId: string, signal?: AbortSignal): Promise<boolean>;

  /** Retry a failed or cancelled render job. */
  retry(runId: string, signal?: AbortSignal): Promise<RenderExecutionHandle>;

  /** Open a realtime progress stream for a running job (returns unsubscribe function).
   *  `onStatus` fires with the stream lifecycle: "connecting" on subscribe,
   *  "open" once the first event arrives, "closed" after a terminal event, and
   *  "error" when the stream errors. Error-precedence: `onError` clears any
   *  prior `progress`/`stage`; `onComplete` clears any prior `error`.
   *
   *  **Status derivation** (from `IClientStreamProtocol.subscribeEvents` callbacks):
   *  - `connecting` — fired synchronously inside `watchProgress` immediately after
   *    `subscribeEvents(...)` is called, before any stream frame arrives.
   *  - `open` — fired on the first `onState` **or** `onProgress` callback, whichever
   *    arrives first. A run that is already terminal when the stream opens still
   *    receives `onState` (with `terminal: true`), which fires `open`; `closed` then
   *    follows from the same callback via the rule below. This guarantees callers
   *    always see `connecting → open → closed` even for terminal-at-open runs.
   *  - `closed` — fired on `onTerminal` **and** on `onState` when `state.terminal === true`
   *    (the latter covers a run that reaches terminal before any `progress` frame,
   *    or a replayed terminal state). If `onState` fires with `terminal: true` as the
   *    very first callback, `open` and `closed` both fire from that single event,
   *    in that order.
   *  - `error` — fired on `onError` (covers both the pre-stream `ApiTransportError`
   *    envelope path and the stream-close-without-terminal `ServerStreamError` path).
   *    `error` is terminal; no further `onStatus` fires after `onError` or `onTerminal`.
   *  - **Pre-stream non-2xx path** — when the stream capability hits a non-2xx response
   *    before any frame arrives (`ApiTransportError` via `normalizeErrorEnvelope`),
   *    `open` does **not** fire because no `onState`/`onProgress` arrives; the sequence
   *    is `connecting → error`. */
  watchProgress(
    runId: string,
    onStatus: (status: "connecting" | "open" | "closed" | "error") => void,
    onState: (state: { stage: string; terminal: boolean }) => void,
    onProgress: (snapshot: ProgressSnapshotVO) => void,
    onComplete: (meta: RenderOutputMetaVO) => void,
    onError: (err: Error) => void
  ): () => void;

  /** Probe service connectivity and status. */
  probeHealth(signal?: AbortSignal): Promise<SystemHealthVO>;

  /** Load system settings and output directory configurations. */
  loadConfig(signal?: AbortSignal): Promise<SystemConfigVO>;
}
```

---

## 5. Feature Folder Specifications (`packages/client/src/`)

`packages/client/` is a feature folder containing business logic and concrete capabilities. It complies with AES403 (Capabilities Role), AES405 (Agent Role), and AES702 (Feature Folder Health).

### 5.1 Capabilities Architecture (`capabilities_client_<feature>.ts`)

Each capability file implements exactly one protocol interface from `contract_client_protocol.ts` and structures its source into the canonical 3-block layout. The `<feature>` token is the concrete capability name: `transport`, `inspect`, `render`, `stream`, `system`. The FRD and BACKLOG sections (§7.1, §7.2) always use the concrete names (`FR-CLIENT-001: Transport`, `FR-CLIENT-002: Inspection`, etc.), never the placeholder, to avoid AES607 lint confusion.
- **Block 1: Type Definitions** (max 3 types/interfaces)
- **Block 2: Protocol Implementation** (implements the protocol)
- **Block 3: Inherent Implementation & Internal Helpers** (stateless private utilities)

#### Capability 1: `capabilities_client_transport.ts`
- **Role:** Concrete HTTP communication layer wrapping global `fetch`.
- **Protocol:** Implements `IClientTransportProtocol`.
- **Logic:**
  - Manages base URL, default headers (`Content-Type: application/json`, `Accept: application/json`), and request abort signals.
  - Automatically parses JSON responses and catches HTTP 4xx/5xx status codes.
  - Unpacks the backend `ApiErrorEnvelope` (defined in `modules/api/src/surface_api_response_view.py`, shaped `{error:{code,message,stage?}}`) and maps it into structured `ApiTransportError` instances via `normalizeErrorEnvelope(status, json)`. The resulting `ApiTransportError` carries `code`, `message`, `status`, `retryable`, and `stage?` (stage is preserved, not dropped).
  - **Retryability derivation rule** (the live envelope has no `retryable` field, so it is inferred from HTTP status): `408`/`425`/`429`/`5xx` → `retryable = true`; `400`/`404`/`422` → `retryable = false`; `409` → `retryable = true` only when `code === "ACTIVE_JOB_CONFLICT"` (retryable-after-completion), otherwise `false`.
  - Handles network failures (raising `NetworkConnectionError`) and timeout aborts. **Timeout scoping:** the transport applies `TIMEOUT_DEFAULT_MS` (10 s) to every request it issues — `get`/`post` for health, config, inspect, start-render, cancel, retry, progress, result, view, and output-meta — by composing `AbortSignal.any([callerSignal, AbortSignal.timeout(TIMEOUT_DEFAULT_MS)])` (caller signal wins if both fire; the timeout aborts are surfaced as `ApiTransportError` with `code = "TIMEOUT"`). This is safe because every transport-issued call is a short request/response exchange; the render lifecycle's multi-minute stages do **not** run inside a single transport call (the orchestrator polls `getView` or subscribes via the stream capability). The **stream capability does not use the transport** and therefore does **not** apply `TIMEOUT_DEFAULT_MS` — it is long-lived and honors only caller abort (see Capability 4).

#### Capability 2: `capabilities_client_inspect.ts`
- **Role:** Handles PSD document inspection operations against `/api/inspect`.
- **Protocol:** Implements `IClientInspectProtocol`.
- **Logic:**
  - Validates `input_path` before dispatching.
  - Communicates via `IClientTransportProtocol.post<InspectResponsePayload>('/inspect', { input_path })`.
  - Maps wire `InspectResponsePayload` → domain `PsdDocumentInfoVO`: copies `valid`, `summary`, `layer_count` → `layerCount`, and maps each `LayerPayload` → `LayerMetadataVO` with `bounds{x,y,width,height}` passed through unchanged.

#### Capability 3: `capabilities_client_render.ts`
- **Role:** Manages the render job lifecycle.
- **Protocol:** Implements `IClientRenderProtocol`.
- **Logic:**
  - `startRender`: POSTs `StartRenderRequest` to `/api/renders`.
  - `getProgress`: GETs `/api/renders/{run_id}/progress`.
  - `getResult`: GETs `/api/renders/{run_id}`.
  - `getView`: GETs `/api/renders/{run_id}/view`.
  - `getOutputMeta`: GETs `/api/renders/{run_id}/output/meta`.
  - `cancelRender`: POSTs `/api/renders/{run_id}/cancel`.
  - `retryRender`: POSTs `/api/renders/{run_id}/retry`.

#### Capability 4: `capabilities_client_stream.ts`
- **Role:** Handles real-time Server-Sent Events (SSE) telemetry.
- **Protocol:** Implements `IClientStreamProtocol`.
- **Transport:** Uses a chunked `fetch` with `ReadableStream` reader (not `EventSource`) against `/api/renders/{run_id}/events`. This choice gives explicit `AbortSignal` abort control, deterministic unit tests with a fake reader, and avoids `EventSource`'s inability to pass custom headers or integrate with caller-provided abort signals.
- **SSE Frame Grammar:** The backend emits standard SSE frames with the following line types:
  - `retry: <ms>\n\n` — sent once as the opening frame; sets the client reconnect interval.
  - `id: <n>\nevent: <name>\ndata: <json>\n\n` — one complete event frame. The `name` is one of `state`, `progress`, or `terminal`. The `data` is a single-line JSON payload (the backend never emits multi-line `data:`). A blank line (`\n\n`) terminates each frame.
  - The capability parses each frame by splitting on `\n\n`, then extracting `id:`, `event:`, and `data:` fields from each frame's lines using `utility_client_parser.ts` `parseSseChunk`.
- **Event Dispatch:**
  - `state` — emitted as the opening frame with the run's current stage (`{stage, run_id, terminal}`). Dispatched to `onState`.
  - `progress` — emitted on each progress tick (`ProgressResponsePayload` shape). Dispatched to `onProgress`.
  - `terminal` — emitted when the run reaches a terminal stage (`RunResultResponsePayload` shape). Dispatched to `onTerminal`. The stream must be closed after receiving this event.
- **Error Handling:** Before streaming begins, the endpoint may return 400/404 as JSON `{error:{code,message,stage?}}`. The capability must detect non-2xx HTTP status, parse the error envelope via `normalizeErrorEnvelope`, and invoke `onError` with the resulting `ApiTransportError`. If the stream closes without a `terminal` event, the capability invokes `onError` with a `ServerStreamError` (this is the sole producer of `ServerStreamError` in the codebase — the capability raises it exactly when the server-side stream closes without having dispatched a `terminal` event, which is the "unexpected disconnect" signal distinct from the non-2xx-before-stream `ApiTransportError` path).
- **Transport independence (intentional):** The stream capability does **not** reuse `IClientTransportProtocol`/`ClientTransportCapability`. SSE needs raw streaming reads (`response.body.getReader()`) that the transport's request/response JSON abstraction cannot provide, so `ClientStreamCapability` is constructed with `baseUrl` (not the shared `transport` instance) and issues its own `fetch`. Because it bypasses the transport, the stream capability must independently reproduce the transport's cross-cutting concerns for its non-2xx path:
  - **(a)** Issue a `fetch` with `Accept: text/event-stream` (plus the same default headers the transport applies), using an `AbortController` whose `signal` is honored for caller abort.
  - **(b)** On a non-2xx response, parse the `{"error":{...}}` envelope via `normalizeErrorEnvelope(status, json)` and invoke `onError` with the resulting `ApiTransportError` (covering the 400/404 envelopes the live `/api/renders/{run_id}/events` returns before streaming starts).
  - **(c)** On unsubscribe, abort the underlying `fetch` via `AbortController.abort()`. A caller-initiated abort is **not** surfaced as an error; only a server-side stream close without a `terminal` event is surfaced as `ServerStreamError`.
  - The capability does **not** apply `TIMEOUT_DEFAULT_MS` (the stream is long-lived); it honors only caller abort.
- **Lifecycle:** Closes the connection automatically upon receiving a terminal event. Returns an unsubscribe function that aborts the underlying `fetch` via `AbortController.abort()`.

#### Capability 5: `capabilities_client_system.ts`
- **Role:** Handles service health checks and configuration queries.
- **Protocol:** Implements `IClientSystemProtocol`.
- **Logic:**
  - `getHealth`: GETs `/api/health`.
  - `getConfig`: GETs `/api/config`.

---

### 5.2 Agent Orchestrator (`agent_client_orchestrator.ts`)

The Agent Orchestrator coordinates multiple capability protocols to fulfill the high-level `IClientAggregate` contract.

#### AES405 Rule Compliance
- **Block Layout:**
  - `// Block 1: Module Declaration` (types and constructor signature)
  - `// Block 2: Module Contract` (implementation of `IClientAggregate`)
  - `// Block 3: Module Helpers` (coordination translation and data mapping)
- **Subsystem Count:** Injects ≥2 subsystem protocols (injects `IClientInspectProtocol`, `IClientRenderProtocol`, `IClientStreamProtocol`, and `IClientSystemProtocol`).
- **No Direct I/O:** Contains no filesystem access, `fetch`, `EventSource`, or network I/O; all operations delegate to injected protocols.
- **Stateless:** Maintains no internal mutable state outside dependency references.
- **No Business Calculation:** Performs orchestration and sequencing only; numeric calculations and raw transformations are offloaded to capabilities or utility functions.

#### Orchestration Workflow

**Inspect flow** (the simplest path — a single request/response round trip):
```text
Surface (e.g. Studio)
       │
       ▼  inspect(inputPath)
┌────────────────────────────────────────────────────────┐
│               ClientOrchestrator                       │
│  (implements IClientAggregate, coordinates protocols)  │
└──────┬──────────────────────┬──────────────────────────┘
       │                      │
       ▼                      ▼
┌──────────────┐       ┌──────────────┐
│   Inspect    │       │  Transport   │
│  Capability  │       │  Capability  │
└──────────────┘       └──────────────┘
       │                      │
       ▼                      ▼
  POST /api/inspect ────► Python FastAPI
```

**Render lifecycle flow** (the orchestrator's primary value-add — sequencing across capabilities, with SSE-preferred and polling-fallback paths, plus cancel/retry branches):
```text
Surface (e.g. Queue)
       │
       ▼  startRender(inputPath, outputPath?)
┌────────────────────────────────────────────────────────┐
│               ClientOrchestrator                       │
│  1. renderCapability.startRender(...) → RenderExecutionHandle
│  2. streamCapability.subscribeEvents(...) (primary)    │
│     └─ on terminal (RunResultResponsePayload from     │
│        renderCapability.getResult inside the stream   │
│        capability): renderCapability.getOutputMeta()  │
│        → watchProgress.onComplete(RenderOutputMetaVO) │
│        = aggregate.fetchResult(meta)                   │
│  3. if stream unavailable/errors:                      │
│     poll renderCapability.getView(runId) every         │
│     POLL_INTERVAL_DEFAULT_MS until terminal stage;     │
│     getView returns RunViewResponsePayload (stage/    │
│     progress/output_path/error) which the orchestrator│
│     maps to a ProgressSnapshotVO for the surface.      │
│  4. the terminal-path RunResultResponsePayload         │
│     (total_frames, fps, manifests, error) is consumed │
│     only inside the stream capability — it is the SSE  │
│     `terminal` event payload and is delivered to       │
│     watchProgress.onComplete after the orchestrator    │
│     translates its video_path/available into a         │
│     RenderOutputMetaVO via renderCapability.getOutput  │
│     Meta(). No IClientAggregate method surfaces the    │
│     raw RunResultResponsePayload; if a future caller  │
│     needs total_frames/fps/manifests, this is the      │
│     natural widening point (see fetchResult note in   │
│     §4.3).                                             │
│  ── branches ──                                        │
│  cancel(runId):   renderCapability.cancelRender(runId) │
│  retry(runId):    renderCapability.retryRender(runId)  │
│                   → new RenderExecutionHandle (new     │
│                     run_id; caller restarts watch)     │
└──────┬──────────────────────┬──────────────────────────┘
       │                      │
       ▼                      ▼
┌──────────────┐       ┌──────────────┐
│   Render     │       │  Transport   │
│  Capability  │       │  Capability  │
└──────────────┘       └──────────────┘
       │                      │
       ▼                      ▼
  /api/renders[...] ──► Python FastAPI
       │
       ▼
┌──────────────┐
│   Stream     │  (SSE — constructed with baseUrl, not
│  Capability  │   transport; owns its own fetch/AbortController)
└──────────────┘
       │
       ▼
  GET /api/renders/{run_id}/events  (chunked fetch, ReadableStream)
```

**Why both paths exist in the orchestrator:** `watchProgress` is the primary path because SSE delivers lower-latency, server-driven progress. `checkProgress` polling is the fallback the orchestrator uses when the stream capability reports an error before a `terminal` event (the `onStatus("error")` branch of `watchProgress`) or when a caller opts out of streaming. The orchestrator owns the "which path" decision; capabilities remain single-responsibility and unaware of the selection logic.

---

### 5.3 Composition Root & DI Wiring (`root_client_container.ts`)

To prevent orphan code violations (AES502, AES503, AES505), `root_client_container.ts` provides the factory that instantiates capabilities and wires them into the orchestrator:

```typescript
import { ClientOrchestrator } from "./agent_client_orchestrator";
import { ClientTransportCapability } from "./capabilities_client_transport";
import { ClientInspectCapability } from "./capabilities_client_inspect";
import { ClientRenderCapability } from "./capabilities_client_render";
import { ClientStreamCapability } from "./capabilities_client_stream";
import { ClientSystemCapability } from "./capabilities_client_system";
import type { IClientAggregate } from "../../shared/src/client/contract_client_aggregate";

export interface ClientContainerConfig {
  readonly baseUrl?: string;
}

export function createClientAggregate(config?: ClientContainerConfig): IClientAggregate {
  const transport = new ClientTransportCapability(config?.baseUrl);
  const inspect = new ClientInspectCapability(transport);
  const render = new ClientRenderCapability(transport);
  // Stream takes `baseUrl` (not `transport`) because SSE needs raw ReadableStream access
  // and must independently normalize its 4xx error envelope (see §5.1 Capability 4).
  const stream = new ClientStreamCapability(config?.baseUrl);
  const system = new ClientSystemCapability(transport);

  return new ClientOrchestrator(inspect, render, stream, system);
}
```
The stream capability is the sole exception to "all capabilities take the shared `transport`" rule: `ClientStreamCapability` is constructed with `config?.baseUrl` and issues its own `fetch`, because SSE requires raw `response.body` access and the transport's JSON request/response abstraction cannot express a long-lived stream. The stream capability independently reproduces the transport's error normalization (via `normalizeErrorEnvelope`) for its non-2xx path. The other four capabilities (`inspect`, `render`, `system`, and the orchestrator's call paths) share the single `transport` instance.

---

## 6. Surface Layer Integration Patterns

### 6.1 Strict Architectural Decoupling
Surface components (`packages/studio/`, `packages/queue/`, `packages/gallery/`, `packages/home/`, `packages/shell/`) must remain pure presentation components:
- **Rule 1:** No surface file may import `capabilities_client_*`, `agent_client_orchestrator`, or global networking routines.
- **Rule 2:** Passive views, layouts, and components consume data snapshots via props and trigger actions via callback functions.
- **Rule 3:** Smart surfaces (React hooks and stores) consume `IClientAggregate`.
- **Rule 4 (passive prop contracts frozen):** PR 4 does **not** change any passive surface's existing prop contract. `QueueSurfaceProps` (`active`, `queued`, `completed`, `onPause`, `onCancel`, `onDownload?`, `activeImageSrc?`), `StudioLandingProps`, and `StudioCanvasProps` are frozen. Smart containers (`QueueContainer`, `StudioContainer`) map `IClientAggregate` snapshots into these existing props; passive components never learn about the aggregate or its VOs. This preserves `packages/queue/tests/unit_queue_component.test.tsx` and any studio component tests without modification — the only PR 4 work is adding the smart container that feeds the existing props from `IClientAggregate`.

### 6.2 Smart Surface Integration: Client Context & Hooks
Smart surfaces obtain the `IClientAggregate` via a React Context provider rather than prop drilling. The provider and hooks live in `packages/shell/src/surface_client_context.tsx` (a smart-surface file — allowed to import `contract_client_aggregate` per §3.2). It exports three symbols:

- `ClientProvider` — React context provider that accepts an `IClientAggregate` instance (supplied by `root_web_main_entry.ts` from `createWebDependencies().client`) and makes it available to descendant smart surfaces.
- `useClient(): IClientAggregate` — context hook that returns the aggregate. Throws if called outside a `ClientProvider`. This is the smart-container entry point: smart surfaces that are always rendered inside `root_web_main_entry.ts`'s `ClientProvider` call it directly.
- `useOptionalClient(): IClientAggregate | null` — returns the aggregate from context, or `null` if no `ClientProvider` is present (does not throw). Used by `useRenderProgress` so its optional-client path works outside a provider.
- `useRenderProgress(runId: string | null, client?: IClientAggregate)` — render-specific hook. Resolution order: if `client` is supplied, use it directly (no context lookup); otherwise fall back to `useOptionalClient()`. If neither is available (no explicit client and no `ClientProvider`), it returns an idle state (`status: "idle"`, all snapshots `null`) rather than throwing, so tests that exercise the explicit-client path can call the hook without wrapping in `<ClientProvider>`. Callers that already hold the aggregate — e.g. tests — may pass it explicitly; smart containers inside the provider may omit it and rely on the context fallback.

Passive surfaces (`surface_*_component.tsx`, `surface_*_view.tsx`, `surface_*_layout.tsx`) never import the context or hooks; they receive already-mapped snapshots and callbacks via props from a smart container (e.g. `StudioContainer`, `QueueContainer`) that sits between the provider and the passive component.

```typescript
// packages/shell/src/surface_client_context.tsx
import { createContext, useContext, useState, useEffect } from "react";
import type { IClientAggregate } from "@shared/client/contract_client_aggregate";
import type { ProgressSnapshotVO, RenderOutputMetaVO } from "@shared/client/taxonomy_client_vo";

const ClientContext = createContext<IClientAggregate | null>(null);

export function ClientProvider({ client, children }: { client: IClientAggregate; children: React.ReactNode }) {
  return <ClientContext.Provider value={client}>{children}</ClientContext.Provider>;
}

export function useClient(): IClientAggregate {
  const client = useContext(ClientContext);
  if (!client) throw new Error("useClient must be used within a ClientProvider");
  return client;
}

export function useOptionalClient(): IClientAggregate | null {
  return useContext(ClientContext);
}

export function useRenderProgress(runId: string | null, client?: IClientAggregate) {
  // Explicit client wins (test path); otherwise fall back to context. The
  // context lookup is via useOptionalClient so it does not throw when no
  // <ClientProvider> is mounted — the explicit-client path works in isolation.
  const contextClient = useOptionalClient();
  const aggregate = client ?? contextClient;
  const [status, setStatus] = useState<"idle" | "connecting" | "open" | "closed" | "error">("idle");
  const [stage, setStage] = useState<string | null>(null);
  const [progress, setProgress] = useState<ProgressSnapshotVO | null>(null);
  const [result, setResult] = useState<RenderOutputMetaVO | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!runId || !aggregate) return;
    // Error-precedence rule: onError clears progress/stage; onComplete clears error.
    const unsubscribe = aggregate.watchProgress(
      runId,
      (next) => setStatus(next),
      (state) => setStage(state.stage),
      (snapshot) => { setProgress(snapshot); setError(null); },
      (meta) => { setResult(meta); setError(null); setStatus("closed"); },
      (err) => { setError(err); setProgress(null); setStage(null); setStatus("error"); }
    );
    return () => unsubscribe();
  }, [aggregate, runId]);

  return { status, stage, progress, result, error };
}
```

`status: "idle"` is a hook-local pre-subscribe sentinel — `watchProgress.onStatus` never emits `"idle"`; consumers treat `"idle"` as "no active subscription yet" (no `runId` or no `aggregate`), distinct from `"connecting"` (subscription in flight).

`root_web_main_entry.ts` wraps the mounted surfaces in `<ClientProvider client={createWebDependencies().client}>` so any smart descendant (smart containers, `useRenderProgress` callers) resolves the aggregate without prop threading.

### 6.3 Wiring in Application Composition Root
In `packages/root_web_container.ts`, replace stubbed `null` fields with live client dependencies:
```typescript
import { createClientAggregate, type ClientContainerConfig } from "./client/src/root_client_container";
import type { IClientAggregate } from "./shared/src/client/contract_client_aggregate";

export interface WebDependencies {
  readonly client: IClientAggregate;
}

export function createWebDependencies(config?: ClientContainerConfig): WebDependencies {
  return {
    client: createClientAggregate(config),
  };
}
```
`packages/root_web_main_entry.ts` initializes `createWebDependencies()`, then wraps the mounted surfaces in `<ClientProvider client={deps.client}>` (imported from `packages/shell/src/surface_client_context.tsx`, see §6.2). Smart containers (`StudioContainer`, `QueueContainer`) call `useClient()` to resolve the aggregate (they always render inside the provider); `useRenderProgress` calls `useOptionalClient()` internally so its explicit-client test path works without a provider. Smart containers then translate aggregate snapshots into the passive surfaces' existing prop contracts:

- **`StudioContainer`** — wraps `StudioLanding` (`surface_studio_landing_component.tsx`), the actual studio route mounted by `root_web_main_entry.ts`. Calls `client.inspect(inputPath)` to populate layer-panel data and threads the resulting `PsdDocumentInfoVO` down via props. Does **not** mutate `StudioLandingProps`/`StudioCanvasProps`.
- **`QueueContainer`** — wraps `QueueSurface` (`surface_queue_component.tsx`). Subscribes via `client.watchProgress(...)` for the active run, calls `client.fetchResult(runId)` on terminal to populate the completed list, and wires `onPause`/`onCancel` to `client.cancel(runId)`. Maps aggregate VOs → `QueueSurfaceProps` fields per the table in PR 4 (e.g. `RenderOutputMetaVO.videoPath` → `CompletedItem.outputPath`).

**`baseUrl` runtime-config sourcing:** `createWebDependencies(config?)` accepts an optional `ClientContainerConfig` and forwards it verbatim to `createClientAggregate(config)`. When called with no argument (`createWebDependencies()`), `createClientAggregate()` falls back to `API_BASE_URL_DEFAULT` (`http://127.0.0.1:8000/api`). For hosted or non-default-port deployments, `root_web_main_entry.ts` passes the configured base URL through the same factory call site — `createWebDependencies({ baseUrl: import.meta.env.VITE_API_BASE_URL })` — rather than reaching past `createWebDependencies` to call `createClientAggregate` directly. The base URL must be in the API's CORS allow-list (`PSD_API_CORS_ORIGINS`); the default loopback regex covers `localhost`/`127.0.0.0/8`/`[::1]` on any port (so the 8000 dev default needs no CORS config), but hosted origins require the env var to be added server-side. The server-side port counterpart is `PSD_API_PORT` (validated 1–65535).

The static `DEMO_ACTIVE`, `DEMO_QUEUED`, `DEMO_COMPLETED` constants and the per-route no-op callbacks (`onPause`, `onCancel`, `onDownload`) in `root_web_main_entry.ts` are deleted in PR 4. Gallery and Home mock data are intentionally left in place — the client aggregate does not yet cover gallery endpoints.

---

## 7. Functional Specifications & Backlog Definition

### 7.1 `packages/client/FRD.md` Structure (AES609 Compliant)
Per AES609, the Functional Requirements Document must follow this exact section sequence:
1. `# FRD — PSD Timelapse Client Feature`
2. `## Feature Overview`: High-level explanation of the client feature folder, its boundary, and communication with `modules/api/`.
3. `## Functional Requirements`:
   - `### FR-CLIENT-001: HTTP Transport & Error Envelope Handling`
   - `### FR-CLIENT-002: PSD Document Inspection`
   - `### FR-CLIENT-003: Render Job Lifecycle Management`
   - `### FR-CLIENT-004: Server-Sent Events Telemetry Streaming`
   - `### FR-CLIENT-005: System Health & Configuration Diagnostics`
   - `### FR-CLIENT-006: Orchestration & Composition Root`
   - Each FR must include:
     - `#### Business Logic`
     - `#### Edge Cases`
     - `#### Technical Specification` — **request/response FRs (001, 002, 003, 005, 006) use a 5-row table** (`Protocol`, `Method`, `Input`, `Output`, `Error`); **FR-CLIENT-004 (the streaming FR) uses a 6-row table** adding an `Event` row (`state`, `progress`, `terminal`). The `Event` row is omitted (not set to `none`) for non-streaming FRs — forcing an empty/`none` `Event` row on FRs that have no SSE channel is template rigidity that creates AES609 review friction.
     - `#### Test`
     - `#### Metric`
4. `## Public Interface`:
   - `### Protocol API`: List all capability protocols (`IClientTransportProtocol`, etc.)
   - `### Aggregate API`: Document `IClientAggregate` and `ClientOrchestrator`
5. `## Reference`: Links to PRD.md, ROADMAP.md, ARCHITECTURE.md, BACKLOG.md.

### 7.2 `packages/client/BACKLOG.md` Structure (AES607 Compliant)
Per AES607, the Backlog document tracks implementation tasks mapped to FR-IDs. The FR-IDs in BACKLOG are in strict 1:1 correspondence with the FRD's `## Functional Requirements` list (001–006); no FR may appear in BACKLOG without a matching `### FR-CLIENT-00N` heading in the FRD, and vice versa.
- `## Progress Overview`
- `## Backlog Status`
  - `### FR-CLIENT-001`: Transport capability implementation & tests
  - `### FR-CLIENT-002`: Inspect capability implementation & tests
  - `### FR-CLIENT-003`: Render capability implementation & tests
  - `### FR-CLIENT-004`: Stream capability implementation & tests
  - `### FR-CLIENT-005`: System capability implementation & tests
  - `### FR-CLIENT-006`: Orchestrator implementation & DI wiring (maps to `agent_client_orchestrator.ts`, `root_client_container.ts`, and the conformance/integration/orchestrator tests; the FRD's FR-CLIENT-006 documents the `IClientAggregate` coordination contract and the composition-root factory that PR 3 ships)
- `## Reference`: Links to PRD, ROADMAP, ARCHITECTURE, FRD.

### 7.3 `packages/shared/src/client/DATA.md` & `BACKLOG.md`
- `DATA.md` specifies all data objects (`DT-CLIENT-001` through `DT-CLIENT-005` for VO, requests, responses, errors, and contracts).
- `BACKLOG.md` tracks data modeling deliverables.

---

## 8. Test Topology & Quality Gates

The test suite resides in `packages/client/tests/`, adhering to AES103 test naming conventions:

| Test File | Category | Verification Focus |
|---|---|---|
| `contract_client_schema.test.ts` | `contract_` | Schema-pinning gate (PR 1). Runs the committed OpenAPI snapshot at `fixtures/openapi.json` (regenerated by `scripts/dump_openapi.py` via a CI step that fails on drift). The snapshot is committed at repo-root `fixtures/openapi.json`; the test reads it via `readFileSync(new URL("../../../fixtures/openapi.json", import.meta.url), "utf-8")` + `JSON.parse` — three `../` segments from `packages/client/tests/contract_client_schema.test.ts` (`../` → `packages/client/`, `../../` → `packages/`, `../../../` → repo root) so the URL resolves to `<repo>/fixtures/openapi.json`. A smoke assertion embedded directly inside `contract_client_schema.test.ts` verifies `fs.existsSync(new URL("../../../fixtures/openapi.json", import.meta.url))` at test time, so a future move of either the test or the fixture is caught immediately rather than as an unhandled `ENOENT`. The assertion mechanism bridges the compile-time/erased-at-runtime gap: TypeScript `interface` declarations are erased at compile time, so a vitest test running under `tsc --noEmit` + `vitest` has no runtime handle on `keyof RunResultResponsePayload`. To enforce full bidirectional exhaustiveness without adding external dependencies, the test declares expected fields as an object map typed as `Record<keyof T, true>` (e.g. `const EXPECTED_RUN_RESULT_FIELDS: Record<keyof RunResultResponsePayload, true> = { run_id: true, state: true, input_path: true, video_path: true, scripting_manifest_path: true, animator_manifest_path: true, total_frames: true, fps: true, error: true };`). In TypeScript, `Record<keyof T, true>` strictly requires every property of `keyof T` to be declared; if any property is missing, `tsc --noEmit` fails with `TS2741: Property 'x' is missing in type ... but required in type 'Record<keyof T, true>'`, and if an extra property is present, it fails with `TS2353: Object literal may only specify known properties`. The helper `const assertFields = (schemaName: string, fields: readonly string[]) => { for (const f of fields) expect(properties[schemaName]).toHaveProperty(f); }` is then invoked with `Object.keys(EXPECTED_RUN_RESULT_FIELDS)` to assert presence against the JSON-Schema properties. This guarantees bidirectional compile-time exhaustiveness with zero new devDeps. Asserts every field declared in the resulting array exists with a compatible JSON-Schema type in the snapshot's `components.schemas.<Name>` entry (`HealthResponse`, `ConfigResponse`, `RunHandleResponse`, `RunResultResponse`, `ProgressResponse`, `CancelResponse`, `RunViewResponse`, `OutputMetaResponse`, `InspectResponse`, `InspectLayerResponse`, `ErrorResponse`). The TS test never imports or calls Python code; the Python side is confined to the `dump_openapi.py` regen script. Fails the build on any field add/remove/type change that the TS taxonomy has not yet caught up with — pinning `PipelineStageVO` to the live `PipelineStage` StrEnum values and the wire request/response shapes before PR 2 capabilities are written. The snapshot is regenerated in CI (a `web-ui` job runs `uv run python scripts/dump_openapi.py` then `git diff --exit-code fixtures/openapi.json` before `npm test`) so the schema-pinning gate and the Python lanes stay decoupled while still catching backend schema drift. The `web-ui` job is added to `.github/workflows/ci.yml` in PR 1 (see Key Decision #6 and PR 1's affected files): the live workspace has no `ci.yml`, so PR 1 creates it with a `web-ui` job. The runner environment is provisioned with `actions/setup-node@v4` (Node 24), `astral-sh/setup-uv@v5` (enabling cache), and `uv python install "3.14"` so `uv` and Python 3.14 are available on `ubuntu-latest`. The job uses **per-step `working-directory`** because subsequent steps require two different working directories: step `npm ci` → `working-directory: packages` (where `package.json` and `root_config_vite_entry.ts` live); step `uv run python scripts/dump_openapi.py` → repo root (default; `scripts/dump_openapi.py` is at repo root and the root `pyproject.toml` makes `uv run` able to import `modules.api.src.root_api_container`); step `git diff --exit-code fixtures/openapi.json` → repo root (`fixtures/openapi.json` is at repo root; running from `packages/` would resolve to the nonexistent `packages/fixtures/openapi.json` and `git diff` would report no diff and the drift gate would silently pass); step `npm test -- --run` → `working-directory: packages`. Concretely the job is:
  ```yaml
  # .github/workflows/ci.yml (excerpt — web-ui job)
  jobs:
    web-ui:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with: { node-version: '24' }
        - name: Install uv
          uses: astral-sh/setup-uv@v5
          with:
            enable-cache: true
        - name: Set up Python
          run: uv python install "3.14"
        - name: Install web deps
          working-directory: packages
          run: npm ci
        - name: Dump OpenAPI snapshot
          run: uv run python scripts/dump_openapi.py        # repo root
        - name: Fail on backend schema drift
          run: git diff --exit-code fixtures/openapi.json   # repo root
        - name: Run web unit + contract tests
          working-directory: packages
          run: npm test -- --run
  ```
  This pins the working directory per step so the gate is enforceable as written, aligning the gate with the `ci.yml: web-ui` row already documented in `AGENTS.md`'s commands table. PR 1 creates `ci.yml` with **only** the `web-ui` job; the other three `ci.yml`-scoped gates documented in `AGENTS.md`'s commands table (`python-tests`, `lint`, `self-lint`) are out of scope for this client redesign and tracked separately, so a reviewer reading "aligns with AGENTS.md" does not assume PR 1 reconstructs the Python/lint/self-lint CI lanes. The TS test uses `@types/node` (already in `root_tsconfig_entry.json` `compilerOptions.types`), so no `resolveJsonModule` tsconfig change is needed and PR 1's only `root_tsconfig_entry.json` edit remains the `client/tests` `include` addition. |
| `contract_client_conformance.test.ts` | `contract_` | Verifies that all capabilities adhere to their respective `IClient*Protocol` interfaces and `ClientOrchestrator` satisfies `IClientAggregate`. |
| `unit_client_transport.test.ts` | `unit_` | Tests `fetch` parameter passing, JSON decoding, status code handling, and error envelope translation — including 400/404/422 (not retryable), 409 `ACTIVE_JOB_CONFLICT` (retryable-after-completion), 408/425/429/5xx (retryable) envelope cases, and `stage` preservation. |
| `unit_client_inspect.test.ts` | `unit_` | Tests validation of input path, delegation to transport, and that `LayerBoundsVO` is `{x,y,width,height}` matching the wire `bounds` object — no normalization/transformation is applied; the capability passes `bounds` through verbatim. |
| `unit_client_render.test.ts` | `unit_` | Tests job start payload dispatch, `getProgress`/`getView` querying, `getOutputMeta` mapping, the stream-only `getResult` path, cancellation, and retry triggers. |
| `unit_client_stream.test.ts` | `unit_` | Tests SSE message parsing, event dispatcher routing, automatic terminal disconnect, reconnection handling, and the 404-before-stream path (non-2xx envelope → `onError` with `ApiTransportError`) and stream-close-without-terminal (`ServerStreamError`). |
| `unit_client_system.test.ts` | `unit_` | Tests `/health` and `/config` response mapping and degraded service states. |
| `unit_client_orchestrator.test.ts` | `unit_` | Tests workflow coordination across mock protocols without network calls, including the error-after-partial-progress path (stream emits `progress` then errors; `watchProgress` invokes `onError` and the hook's precedence rule clears `progress`/`stage`), the already-terminal-at-stream-open path (stream emits `state` with `terminal: true` as its first frame; `watchProgress` fires `connecting` synchronously, then `open` and `closed` from that single `onState` callback, in that order — no preceding `open` from a progress frame), and the error-before-open path (stream capability invokes `onError` with `ApiTransportError` before any `onState`/`onProgress`; `watchProgress` fires `connecting` then `error`, never `open`). |
| `integration_client_flow.test.ts` | `integration_` | Tests end-to-end client flows against the in-repo `node:http` mock server (`fixture_client_mock_server.ts` — see "Integration-test harness" below). Covers: `startRender` → `watchProgress` (SSE `state`→`progress`→`terminal` sequence) → `fetchResult`; `checkProgress` polling fallback when the SSE stream is not used; `cancel` on an active run; `retry` on a terminal run; and the non-2xx-before-stream error path (mock returns 404 with the `{"error":{...}}` envelope; `watchProgress` invokes `onError` with `ApiTransportError`). |

### Integration-test harness

The live `packages/package.json` devDependencies contain **no MSW** and **no fake-HTTP-server library** (only `vitest`, `jsdom`, `@testing-library/*`, `typescript`, `vite`). `integration_client_flow.test.ts` as originally described ("against a mock HTTP/SSE server (e.g. MSW or Vitest fake HTTP server)") is therefore not implementable without adding a dependency. Two dependency-light options were evaluated:

1. **Chosen — in-repo `node:http` fixture (`fixture_client_mock_server.ts`, zero new deps).** A ~80-line TypeScript helper that calls Node 24's built-in `node:http` `createServer` to serve canned responses on an ephemeral port (`server.listen(0)` then read `server.address().port`). It exposes typed route handlers for each `/api/*` endpoint the aggregate calls, returns the live wire shapes (matching `surface_api_schema_view.py`), and writes SSE frames (`retry: 1000\n\n` + `id: 1\nevent: state\ndata: {...}\n\n` + … + `id: N\nevent: terminal\ndata: {...}\n\n`) for `/api/renders/{run_id}/events`. The test starts the fixture in `beforeAll`, points `createClientAggregate({ baseUrl })` at it, and asserts the full lifecycle. No `package.json` change is needed; PR 3 ships only `fixture_client_mock_server.ts` + `integration_client_flow.test.ts`.

2. **Alternative (not chosen) — `vitest` + `undici` `MockAgent`.** `undici` ships inside Node 24's `node:` runtime but is not a direct `package.json` devDep; using `import { MockAgent } from "undici"` would require adding `"undici": "^6"` to `packages/package.json` devDependencies and wiring `setGlobalDispatcher`. This gives per-request interceptors without a real socket but adds a dependency and a global-dispatcher side effect that must be reset in `afterEach`. Rejected for PR 3 because the `node:http` fixture is simpler, has zero install cost, and exercises the real `fetch` path (closer to production behavior).

**Decision:** PR 3 uses option 1 (`fixture_client_mock_server.ts`). If a future PR needs request-level interception (e.g. simulating flaky SSE mid-stream), option 2 can be added then as a separate devDep bump. `packages/package.json` is **not** modified by PR 3.

---

## Open Questions

None. All architectural decisions regarding folder placement, role suffixes, protocol boundaries, and surface integration are fully resolved.

---

## Key Decisions

1. **Client is a Feature Folder, Not a Surface:**
   - **Decision:** Place client business logic under `packages/client/` containing capabilities and an agent orchestrator, accompanied by an `FRD.md` and `BACKLOG.md`.
   - **Rationale:** The client owns domain operations (API transport, polling, SSE streaming, error translation, inspection caching). Grouping this under a feature folder satisfies AES702 and keeps surface packages pure presentation layers per AES703.

2. **Two-Location Split for Purity (Shared vs. Feature):**
   - **Decision:** Place taxonomy, contracts, and stateless utilities under `packages/shared/src/client/`, while placing capabilities, orchestrator, container, and tests under `packages/client/`.
   - **Rationale:** Complies with AES701 (Shared Folder Purity) and AES702 (Feature Folder Health). Surfaces can import contracts and value objects from shared without taking a dependency on concrete feature implementations.

   - **Promoting capabilities to a top-level `packages/client/` package (vs. a subfolder of `packages/shared/src/client/`):** A separate top-level package enforces a hard AES702 feature-folder boundary so surfaces cannot accidentally import concrete capabilities via a relative path (`../../shared/src/client/capabilities_client_*`). It also lets `@client` be aliased in `root_config_vite_entry.ts` and locked down in `root_tsconfig_entry.json` `paths`, making accidental surface→capability imports fail at compile time. The existing workspace already uses one-package-per-surface (studio, queue, gallery, home, shell); `packages/client/` follows that pattern as the feature-logic peer of the surface packages.

   - **Package manifest & tsconfig:** `packages/client/` is intentionally a **virtual package** — it has **no** `package.json` and **no** `tsconfig.json` of its own. It is compiled solely via the root `packages/root_tsconfig_entry.json` (which gains `client/tests` in `include` in PR 1, plus `@client/*` path mapping and `client/src` in `include` in PR 4 — the split exists so PR 1's `contract_client_schema.test.ts` is typechecked by `tsc -p root_tsconfig_entry.json --noEmit` from the PR that introduces it, closing the PR 1–3 typecheck gap) and tested via the root `vitest` config in `packages/root_config_vite_entry.ts` (whose default `include` glob already covers `*/tests/**/*.test.ts?(x)`). This mirrors how `packages/shared/` and the surface packages are compiled today — all TypeScript in `packages/` is checked by the single root `tsc -p root_tsconfig_entry.json --noEmit` gate and run by the single root `vitest` invocation. No per-package build step is introduced.

3. **Surface Layer Decoupled via Contract Aggregate:**
   - **Decision:** Surface components (Studio, Queue, Gallery, Home, Shell) access the Python backend strictly through `IClientAggregate`.
   - **Rationale:** Completely eliminates direct surface-to-network coupling, enforces AES406, and allows UI components to be unit tested in isolation using lightweight aggregate mocks.

4. **Multi-Protocol Subsystem Architecture:**
   - **Decision:** Decompose client capabilities into 5 focused modules (`transport`, `inspect`, `render`, `stream`, `system`) rather than a monolithic client class.
   - **Rationale:** Ensures compliance with AES403 (single protocol per capability, max 3 types per file) and AES405 (`subsystem_count >= 2` injected into the agent orchestrator).

5. **SSE Stream with Clean Unsubscribe Semantics:**
   - **Decision:** Wrap backend server-sent events (`/api/renders/{run_id}/events`) in `capabilities_client_stream.ts` returning a clean teardown function.
   - **Rationale:** Enables direct lifecycle binding to React hooks (`useEffect` cleanup) while preventing memory leaks and orphaned connections in the browser.

6. **Wire-Contract Pinning via PR 1 Schema-Pinning Test:**
   - **Decision:** PR 1 ships three files that together form the schema-pinning gate: (a) `scripts/dump_openapi.py`, a Python regen script that imports the live `modules/api` FastAPI app in-process (`ApiContainer().app.openapi()`) and writes the serialized OpenAPI document to `fixtures/openapi.json`; (b) `packages/client/tests/contract_client_schema.test.ts`, a TypeScript vitest test that reads the committed snapshot at repo-root `fixtures/openapi.json` via `readFileSync(new URL("../../../fixtures/openapi.json", import.meta.url), "utf-8")` + `JSON.parse` — three `../` segments are required because the test lives at `packages/client/tests/contract_client_schema.test.ts` (`../` → `packages/client/`, `../../` → `packages/`, `../../../` → repo root) and `@types/node` is already in `root_tsconfig_entry.json` `compilerOptions.types`, so no `resolveJsonModule` change is needed — and asserts every field declared in the TS taxonomy (`taxonomy_client_response.ts`, `taxonomy_client_request.ts`, `taxonomy_client_vo.ts`) exists with a compatible JSON-Schema type in the snapshot's `components.schemas.<Name>`. Because TS `interface` declarations are erased at compile time, the test uses an object map typed as `Record<keyof T, true>` to enforce bidirectional compile-time exhaustiveness: e.g. declaring `const EXPECTED_FIELDS: Record<keyof RunResultResponsePayload, true> = { run_id: true, ... }` and asserting each field from `Object.keys(EXPECTED_FIELDS)` exists in `snapshot.components.schemas[schemaName].properties`. In TypeScript, `Record<keyof T, true>` strictly requires every property of `keyof T` to be declared; if any property is missing, `tsc --noEmit` fails with `TS2741`, and if an extra property is present, it fails with `TS2353`, guaranteeing the test field map stays exhaustive and in sync with the interface without adding external devDeps (`expect-type`, `tsd`, `ts-morph`, etc. are not introduced). A smoke assertion embedded directly inside `contract_client_schema.test.ts` (`fs.existsSync(new URL("../../../fixtures/openapi.json", import.meta.url))`) catches a future move of either the test or the fixture as a test failure rather than an unhandled `ENOENT`. And (c) `.github/workflows/ci.yml` (new), whose `web-ui` job installs `uv` via `astral-sh/setup-uv@v5` (cache enabled) and Python 3.14 via `uv python install "3.14"`, installs web dependencies with `npm ci` (`working-directory: packages`), runs `uv run python scripts/dump_openapi.py` at repo root, checks for drift via `git diff --exit-code fixtures/openapi.json` at repo root, and runs `npm test -- --run` (`working-directory: packages`). This provisions `uv` and Python on `ubuntu-latest` and pins the working directory per step so the gate is enforceable as written, and backend schema drift fails CI immediately. The live workspace has no `ci.yml`, so PR 1 creates it — this is what makes the regen step enforceable (the original N1 blocker was relocated from "TS test imports Python" to "CI step references a job that does not exist"; creating the `web-ui` job resolves it). PR 1 creates `ci.yml` with **only** the `web-ui` job; the other three `ci.yml`-scoped gates documented in `AGENTS.md`'s commands table (`python-tests`, `lint`, `self-lint`) are out of scope for this client redesign and tracked separately, so a reviewer reading "aligns with AGENTS.md" does not assume PR 1 reconstructs the Python/lint/self-lint CI lanes. The TS test never imports or calls Python code — the Python side is confined to the regen script. The gate pins `PipelineStageVO` to the live `PipelineStage` StrEnum values (`idle, validating, planning, animating, compositing, encoding, completed, failed, cancelled`) sourced from `modules/shared/src/common/taxonomy_pipeline_state_vo.py`, and pins the wire request/response shapes against `modules/api/src/surface_api_schema_view.py`.
   - **Rationale:** The C1/A2/A3/A4/A5 wire-type divergences from the live backend would have been caught before PR 2 if this gate had existed. Placing it in PR 1 (not PR 2) keeps PR 1 independently valuable — it is the contract layer's own acceptance test — and prevents an implementer from coding PR 2 capabilities against drifted types. The committed-snapshot form (rather than a TS test that imports the FastAPI app in-process, which is not implementable — there is no JS binding to a Python object) keeps the web vitest lane and the Python pytest lane decoupled per `AGENTS.md`/`ci.yml`, while the `web-ui` job's regen step ensures a backend schema change still fails CI immediately. This is the single mechanism that enforces B5's "require a contract test" and A6's "schema-pinning gate" recommendations in one place.

---

## PR Plan

The implementation is broken into four concrete, ordered, independently reviewable and mergeable Pull Requests:

### PR 1: Shared Client Contracts & Taxonomy
- **Title:** `feat(shared): establish client contracts, taxonomy, and utilities`
- **Affected Files:**
  - `packages/shared/src/client/DATA.md`
  - `packages/shared/src/client/BACKLOG.md`
  - `packages/shared/src/client/taxonomy_client_constant.ts`
  - `packages/shared/src/client/taxonomy_client_vo.ts`
  - `packages/shared/src/client/taxonomy_client_request.ts`
  - `packages/shared/src/client/taxonomy_client_response.ts`
  - `packages/shared/src/client/taxonomy_client_error.ts`
  - `packages/shared/src/client/contract_client_protocol.ts`
  - `packages/shared/src/client/contract_client_aggregate.ts`
  - `packages/shared/src/client/utility_client_url.ts`
  - `packages/shared/src/client/utility_client_parser.ts`
  - `scripts/dump_openapi.py` (OpenAPI snapshot regen script — see §8 and Key Decision #6)
  - `fixtures/openapi.json` (committed OpenAPI snapshot read by the schema-pinning test)
  - `packages/client/tests/contract_client_schema.test.ts` (schema-pinning gate — see §8)
  - `packages/root_tsconfig_entry.json` (add `client/tests` to `include` — see note below)
  - `.github/workflows/ci.yml` (new — `web-ui` job with runner setup via `actions/setup-node@v4`, `astral-sh/setup-uv@v5`, and `uv python install "3.14"`, followed by per-step `working-directory`: `npm ci` in `packages/`, `uv run python scripts/dump_openapi.py` at repo root, `git diff --exit-code fixtures/openapi.json` at repo root, `npm test -- --run` in `packages/`; creates `ci.yml` with **only** the `web-ui` job — `python-tests`, `lint`, and `self-lint` are out of scope and tracked separately; see §8, Key Decision #6)
- **Dependencies:** None.
- **Description:** Scaffolds the shared client domain in `packages/shared/src/client/`. Defines all data models, error classes, route constants, stateless parsing/URL utilities, and the TypeScript interfaces for subsystem protocols (`IClient*Protocol`) and the aggregate contract (`IClientAggregate`). Documents specs in `DATA.md` and `BACKLOG.md`. Ships a schema-pinning contract test (`packages/client/tests/contract_client_schema.test.ts`) that reads the committed OpenAPI snapshot at repo-root `fixtures/openapi.json` via `readFileSync(new URL("../../../fixtures/openapi.json", import.meta.url), "utf-8")` + `JSON.parse` — three `../` segments are required because the test lives at `packages/client/tests/contract_client_schema.test.ts` (`../` → `packages/client/`, `../../` → `packages/`, `../../../` → repo root) and `@types/node` is already present in `root_tsconfig_entry.json` `compilerOptions.types`. A smoke assertion embedded directly inside `contract_client_schema.test.ts` (`fs.existsSync(new URL("../../../fixtures/openapi.json", import.meta.url))`) catches a future move of either the test or the fixture as a test failure rather than an unhandled `ENOENT`. Because TS `interface` declarations are erased at compile time, the test uses an object map typed as `Record<keyof T, true>` to enforce bidirectional compile-time exhaustiveness: e.g. declaring `const EXPECTED_FIELDS: Record<keyof RunResultResponsePayload, true> = { run_id: true, state: true, ... }` and asserting each field from `Object.keys(EXPECTED_FIELDS)` exists with a compatible JSON-Schema type in the snapshot's `components.schemas.<Name>` entry. In TypeScript, `Record<keyof T, true>` strictly requires every property of `keyof T` to be declared; if any property is missing, `tsc --noEmit` fails with `TS2741`, and if an extra property is present, it fails with `TS2353`, ensuring the field list stays exhaustive and strictly coupled to the interface without adding external devDeps. The snapshot is produced by `scripts/dump_openapi.py`, which imports the live FastAPI app in-process (`ApiContainer().app.openapi()`) and writes the serialized document — the TS test never imports or calls Python code. A CI step regenerates the snapshot (`uv run python scripts/dump_openapi.py`) and runs `git diff --exit-code fixtures/openapi.json` before `npm test` so backend schema drift fails CI immediately. Because the live workspace has no `ci.yml` (only `auto-merge.yml`, `auto-release.yml`, `nightly.yml`, `release.yml`, `tag-release-prs.yml` exist under `.github/workflows/`), PR 1 also **creates** `.github/workflows/ci.yml` with a `web-ui` job. The job configures Node 24 (`actions/setup-node@v4`), installs `uv` (`astral-sh/setup-uv@v5` with cache enabled), and installs Python 3.14 (`uv python install "3.14"`). It then uses **per-step `working-directory`** because subsequent steps require two different working directories: step `npm ci` → `working-directory: packages` (where `package.json` and `root_config_vite_entry.ts` live); step `uv run python scripts/dump_openapi.py` → repo root (default; `scripts/dump_openapi.py` is at repo root and the root `pyproject.toml` makes `uv run` able to import `modules.api.src.root_api_container`); step `git diff --exit-code fixtures/openapi.json` → repo root (`fixtures/openapi.json` is at repo root; running from `packages/` would resolve to the nonexistent `packages/fixtures/openapi.json` and the drift gate would silently pass); step `npm test -- --run` → `working-directory: packages`. This provisions the necessary tools on `ubuntu-latest` and pins the working directory per step so the gate is enforceable as written, and makes the regen step enforceable. PR 1 creates `ci.yml` with **only** the `web-ui` job; the other three `ci.yml`-scoped gates documented in `AGENTS.md`'s commands table (`python-tests`, `lint`, `self-lint`) are out of scope for this client redesign and tracked separately, so a reviewer reading "aligns with AGENTS.md" does not assume PR 1 reconstructs the Python/lint/self-lint CI lanes. The TS test reads the committed snapshot using `@types/node` (already present in `root_tsconfig_entry.json` `compilerOptions.types`), so no `resolveJsonModule` compilerOptions change is required and PR 1's only `root_tsconfig_entry.json` edit remains the `client/tests` `include` addition. This gate keeps PR 1 independently valuable: it fails the build the moment a future backend schema change (or a TS taxonomy drift) would silently break PR 2's capabilities. The test file lives under `packages/client/tests/` (picked up by the root vitest `include` glob `*/tests/**/*.test.ts?(x)`) even though PR 1 only ships shared contracts, because the test's subject is the shared taxonomy it pins. The `@client/*` path mapping is deferred to PR 4 (no PR 1–3 file imports through it); only the `client/tests` `include` entry is added now so the schema test is typechecked by `tsc -p root_tsconfig_entry.json --noEmit` from the PR that introduces it, closing the three-PR typecheck gap flagged in review.

### PR 2: Client Capabilities Implementation
- **Title:** `feat(client): implement client capabilities and transport layer`
- **Affected Files:**
  - `packages/client/FRD.md`
  - `packages/client/BACKLOG.md`
  - `packages/client/src/capabilities_client_transport.ts`
  - `packages/client/src/capabilities_client_inspect.ts`
  - `packages/client/src/capabilities_client_render.ts`
  - `packages/client/src/capabilities_client_stream.ts`
  - `packages/client/src/capabilities_client_system.ts`
  - `packages/client/tests/unit_client_transport.test.ts`
  - `packages/client/tests/unit_client_inspect.test.ts`
  - `packages/client/tests/unit_client_render.test.ts`
  - `packages/client/tests/unit_client_stream.test.ts`
  - `packages/client/tests/unit_client_system.test.ts`
- **Dependencies:** PR 1.
- **Description:** Implements the 5 concrete capability classes under `packages/client/src/` adhering to the AES 3-block structure and protocol contracts. Adds `FRD.md` and `BACKLOG.md` for the client feature folder. Implements thorough unit test coverage with mock HTTP and SSE streams.

### PR 3: Client Agent Orchestrator & DI Container
- **Title:** `feat(client): introduce agent orchestrator, root container, and conformance tests`
- **Affected Files:**
  - `packages/client/FRD.md`
  - `packages/client/BACKLOG.md`
  - `packages/client/src/agent_client_orchestrator.ts`
  - `packages/client/src/root_client_container.ts`
  - `packages/client/src/index.ts`
  - `packages/client/tests/unit_client_orchestrator.test.ts`
  - `packages/client/tests/contract_client_conformance.test.ts`
  - `packages/client/tests/integration_client_flow.test.ts`
  - `packages/client/tests/fixture_client_mock_server.ts` (integration-test harness — see §8 "Integration-test harness")
- **Dependencies:** PR 2.
- **Description:** Implements `ClientOrchestrator` coordinating all injected capabilities without direct I/O. Builds the local DI container in `root_client_container.ts` and barrel exports in `index.ts`. Adds protocol conformance tests, orchestrator unit tests, and multi-capability integration tests. The integration test harness (`fixture_client_mock_server.ts`) is a tiny in-repo `node:http` fixture (zero new dependencies) that serves canned JSON/SSE responses for `/api/health`, `/api/config`, `/api/inspect`, `/api/renders`, `/api/renders/{run_id}/progress`, `/api/renders/{run_id}/events`, and `/api/renders/{run_id}` so `integration_client_flow.test.ts` can drive `IClientAggregate` end-to-end without a running Python backend. See §8 "Integration-test harness" for the full specification and the dependency-light alternatives considered.

### PR 4: Surface Layer Integration & Root DI Wiring
- **Title:** `feat(web): wire client aggregate into root DI container and connect surface hooks`
- **Affected Files:**
  - `packages/root_config_vite_entry.ts` (add `@client` → `client/src` alias)
  - `packages/root_tsconfig_entry.json` (add `@client/*` path mapping + `client/src` to `include`; `client/tests` was added in PR 1)
  - `packages/root_web_container.ts`
  - `packages/root_web_main_entry.ts`
  - `packages/shell/src/surface_client_context.tsx`
  - `packages/studio/src/surface_studio_landing_component.tsx`
  - `packages/queue/src/surface_queue_component.tsx`
  - `packages/queue/tests/unit_queue_component.test.tsx` (confirm unchanged; run to verify passive contract frozen)
  - `packages/shell/tests/integration_shell_frame.test.tsx`
- **Dependencies:** PR 3.
- **Description:** Adds `@client` Vite resolve alias and tsconfig path mapping so `tsc --noEmit` and Vite dev/build resolve `packages/client/src` imports. Replaces the legacy null stubs in `root_web_container.ts` with live client dependencies. Introduces smart surface client hooks to connect the actually-mounted Studio and Queue surfaces to the Python backend via `IClientAggregate`. Replaces static mock data (`DEMO_ACTIVE`, `DEMO_QUEUED`, `DEMO_COMPLETED` in `root_web_main_entry.ts`) with live API state while preserving passive component purity.
- **Studio surface scope:** The live studio route is mounted via `StudioLanding` (`surface_studio_landing_component.tsx`), not `StudioCanvas` directly. `StudioCanvas` is rendered *inside* `StudioLanding` and takes no data props today; PR 4 does **not** extend `StudioCanvas`'s prop contract (it remains a static layout). Instead, the studio smart container wraps `StudioLanding` and supplies it the `PsdDocumentInfoVO`/progress snapshots it needs. `surface_studio_landing_component.tsx` is added to PR 4's affected-files list to host the smart container. If a future PR wants to wire `StudioCanvas` itself, that is out of scope here.
- **Queue surface scope & prop mapping:** `QueueSurface` already follows passive purity with `QueueSurfaceProps` (`active`, `queued`, `completed`, `onPause`, `onCancel`, `onDownload?`, `activeImageSrc?`). PR 4 does **not** change `QueueSurfaceProps`; it adds a smart container (`QueueContainer`) that subscribes to `IClientAggregate.watchProgress` + `fetchResult` and maps aggregate snapshots into the existing snake_case surface-local types:
  - `ProgressSnapshotVO.runId` → `RunHandle.run_id`
  - `ProgressSnapshotVO.stage` → `ProgressSnapshot.stage`
  - `ProgressSnapshotVO.current/total/percent/message` → `ProgressSnapshot.current/total/percent/message`
  - `RenderOutputMetaVO.videoPath` → `CompletedItem.outputPath`
  - `RenderOutputMetaVO.sizeBytes` → `CompletedItem.sizeBytes`
  - `startRender`'s `RenderExecutionHandle.runId/state/inputPath` → `RunHandle.run_id/state/input_path`
  This keeps `packages/queue/tests/unit_queue_component.test.tsx` passing unchanged (the passive component's prop contract is frozen; only the smart container feeding it changes).
- **Root mock-data removal:** `root_web_main_entry.ts` holds `DEMO_ACTIVE`, `DEMO_QUEUED`, `DEMO_COMPLETED`, and the per-route no-op callbacks (`onPause`, `onCancel`, `onDownload`). PR 4 replaces these with the smart containers (`StudioContainer`, `QueueContainer`) wired to `createWebDependencies().client`. The static `DEMO_*` constants are deleted. Gallery/Home mock data is out of scope for PR 4 (no live gallery endpoint is wired by the client aggregate).
