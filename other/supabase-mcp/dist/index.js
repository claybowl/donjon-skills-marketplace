#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import { Client } from "pg";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
// Database connection
const getDbClient = () => {
    const password = process.env.SUPABASE_DB_PASSWORD;
    const projectRef = process.env.SUPABASE_PROJECT_REF || "wexuzgrgpuuynirloryg";
    if (!password) {
        throw new Error("SUPABASE_DB_PASSWORD environment variable required");
    }
    return new Client({
        host: `db.${projectRef}.supabase.co`,
        port: 5432,
        database: "postgres",
        user: "postgres",
        password: password,
        ssl: {
            rejectUnauthorized: false
        }
    });
};
// Tool definitions
const tools = [
    {
        name: "query",
        description: "Execute SQL query on the database",
        inputSchema: {
            type: "object",
            properties: {
                sql: {
                    type: "string",
                    description: "SQL query to execute"
                }
            },
            required: ["sql"]
        }
    },
    {
        name: "get_tables",
        description: "List all tables in the database",
        inputSchema: {
            type: "object",
            properties: {}
        }
    },
    {
        name: "get_table_schema",
        description: "Get schema for a specific table",
        inputSchema: {
            type: "object",
            properties: {
                table: {
                    type: "string",
                    description: "Table name"
                }
            },
            required: ["table"]
        }
    },
    {
        name: "run_migration",
        description: "Execute SQL migration from file",
        inputSchema: {
            type: "object",
            properties: {
                migration_file: {
                    type: "string",
                    description: "Path to SQL migration file"
                }
            },
            required: ["migration_file"]
        }
    }
];
// Server setup
const server = new Server({
    name: "supabase-mcp",
    version: "1.0.0"
});
// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return { tools };
});
// Call tool
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const client = getDbClient();
    try {
        await client.connect();
        switch (name) {
            case "query": {
                const { sql } = z.object({ sql: z.string() }).parse(args);
                const result = await client.query(sql);
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify(result.rows, null, 2)
                        }
                    ]
                };
            }
            case "get_tables": {
                const result = await client.query(`
          SELECT table_name 
          FROM information_schema.tables 
          WHERE table_schema = 'public'
          ORDER BY table_name
        `);
                return {
                    content: [
                        {
                            type: "text",
                            text: result.rows.map(r => r.table_name).join("\n")
                        }
                    ]
                };
            }
            case "get_table_schema": {
                const { table } = z.object({ table: z.string() }).parse(args);
                const result = await client.query(`
          SELECT column_name, data_type, is_nullable
          FROM information_schema.columns
          WHERE table_name = $1 AND table_schema = 'public'
          ORDER BY ordinal_position
        `, [table]);
                return {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify(result.rows, null, 2)
                        }
                    ]
                };
            }
            case "run_migration": {
                const { migration_file } = z.object({ migration_file: z.string() }).parse(args);
                const sql = fs.readFileSync(migration_file, "utf8");
                await client.query(sql);
                return {
                    content: [
                        {
                            type: "text",
                            text: `Migration executed successfully: ${path.basename(migration_file)}`
                        }
                    ]
                };
            }
            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${errorMessage}`
                }
            ],
            isError: true
        };
    }
    finally {
        await client.end();
    }
});
// Start server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
}
main().catch(console.error);
//# sourceMappingURL=index.js.map