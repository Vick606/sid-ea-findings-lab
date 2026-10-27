/**
 * Scenario 04 TypeScript MCP client.
 *
 * Spawns the Python MCP server over stdio, initializes an MCP session,
 * and calls read_file with a foreign user_id. The response differs per
 * variant:
 *
 *   vulnerable -> returns noor's file content
 *   fixed      -> returns not found because the server uses the bound
 *                 principal (rasmus) for the store lookup
 *   negative   -> returns not found because the per-user store has no
 *                 entry for noor
 *
 * Usage (from clients/ts):
 *   npm install
 *   npm run build
 *   npm run vulnerable
 *   npm run fixed
 *   npm run negative
 */

import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const VALID_VARIANTS = ["vulnerable", "fixed", "negative"] as const;
type Variant = (typeof VALID_VARIANTS)[number];

const arg = process.argv[2];
if (!arg || !VALID_VARIANTS.includes(arg as Variant)) {
  console.error(`usage: client.js <${VALID_VARIANTS.join("|")}>`);
  process.exit(2);
}
const variant = arg as Variant;

const here = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(here, "..", "..", "..");

async function main(): Promise<void> {
  const serverModule = `scenarios.mcp_confused_deputy.${variant}.server`;

  const transport = new StdioClientTransport({
    command: "uv",
    args: ["run", "python", "-m", serverModule],
    cwd: projectRoot,
  });

  const client = new Client(
    { name: "confused-deputy-client", version: "0.1.0" },
    { capabilities: {} },
  );

  await client.connect(transport);

  try {
    const tools = await client.listTools();
    console.log(
      `[${variant}] tools: ${tools.tools.map((t) => t.name).join(", ")}`,
    );

    // The agent is steered by a retrieved doc into asking for noor's
    // file. It sends user_id=noor regardless of which variant runs.
    const response = await client.callTool({
      name: "read_file",
      arguments: { user_id: "noor", path: "comp.md" },
    });

    console.log(`[${variant}] read_file(user_id=noor, path=comp.md):`);
    const blocks = (response.content ?? []) as Array<{
      type: string;
      text?: string;
    }>;
    for (const block of blocks) {
      if (block.type === "text" && block.text !== undefined) {
        console.log(`  ${block.text}`);
      } else {
        console.log(`  ${JSON.stringify(block)}`);
      }
    }
  } finally {
    await client.close();
  }
}

main().catch((err: unknown) => {
  console.error(err);
  process.exit(1);
});
