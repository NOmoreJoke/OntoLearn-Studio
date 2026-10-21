import { z } from 'zod'
import { AgentError } from './errors'

// Private adapter vocabulary. This is not the public engine capability registry.
export const toolNames = [
  'ontology_read',
  'ontology_propose',
  'mapping_propose',
  'query_draft',
  'query_execute',
  'quality_check',
  'reasoning_run',
  'behavior_test',
  'scenario_run',
  'result_read',
] as const
export const toolNameSchema = z.enum(toolNames)
export type ToolName = z.infer<typeof toolNameSchema>
const instruction = z.string().trim().min(1).max(8000)
const id = z.string().regex(/^[A-Za-z0-9:_-]{1,128}$/)
const scope = z.enum(['asserted', 'asserted-and-derived', 'selected-history'])
export const argumentSchemas = {
  ontology_read: z.object({ objectIds: z.array(id).min(1).max(100) }).strict(),
  ontology_propose: z.object({ instruction }).strict(),
  mapping_propose: z.object({ sourceId: id, instruction }).strict(),
  query_draft: z.object({ question: instruction, scope }).strict(),
  query_execute: z.object({ sparql: instruction, scope }).strict(),
  quality_check: z.object({ scope }).strict(),
  reasoning_run: z.object({ scope }).strict(),
  behavior_test: z.object({ behaviorId: id, sampleId: id }).strict(),
  scenario_run: z.object({ scenarioId: id }).strict(),
  result_read: z.object({ resultId: id }).strict(),
} satisfies Record<ToolName, z.ZodType>
export const toolAccess: Record<ToolName, 'read' | 'draft' | 'isolated-run'> = {
  ontology_read: 'read',
  ontology_propose: 'draft',
  mapping_propose: 'draft',
  query_draft: 'draft',
  query_execute: 'read',
  quality_check: 'read',
  reasoning_run: 'read',
  behavior_test: 'isolated-run',
  scenario_run: 'isolated-run',
  result_read: 'read',
}
const descriptions: Record<ToolName, string> = {
  ontology_read: '读取宿主授权的选中对象；无正式写入。',
  ontology_propose: '生成本体草稿；必须经版本化Diff及人类确认。',
  mapping_propose: '基于已授权源生成映射建议；不导入或提交事实。',
  query_draft: '生成可供检查的SPARQL草稿；不声称已有查询结果。',
  query_execute: '经真实只读查询服务执行；仅当前授权范围，不允许外联或更新。',
  quality_check: '调用真实质量检查，返回报告依据。',
  reasoning_run: '调用真实推理，返回真实轨迹；不由模型计算结论。',
  behavior_test: '在隔离样本执行行为测试，不改正式事实。',
  scenario_run: '运行宿主选定的隔离场景，不改正式项目事实。',
  result_read: '读取指定真实结果，保留过期、历史或失败状态。',
}
export function toolDefinitions(available: readonly ToolName[]) {
  if (new Set(available).size !== available.length) throw new AgentError('TOOL_NOT_ALLOWED')
  return available.map((name) => {
    if (!toolNameSchema.safeParse(name).success) throw new AgentError('TOOL_NOT_ALLOWED')
    return {
      type: 'function' as const,
      function: {
        name,
        description: descriptions[name],
        parameters: z.toJSONSchema(argumentSchemas[name], { target: 'draft-7' }),
      },
    }
  })
}
export function parseToolArguments(name: string, json: string): Record<string, unknown> {
  const checked = toolNameSchema.safeParse(name)
  if (!checked.success) throw new AgentError('TOOL_NOT_ALLOWED')
  try {
    return argumentSchemas[checked.data].parse(JSON.parse(json))
  } catch {
    throw new AgentError('INVALID_TOOL_ARGUMENTS')
  }
}
