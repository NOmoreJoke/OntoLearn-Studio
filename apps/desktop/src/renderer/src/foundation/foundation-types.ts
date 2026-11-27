import {
  RETAIL_NS,
  type FoundationMicroStepId,
} from '../learning/scenarios/retail-membership-orders'

export type SandboxMode = 'excel' | 'clinic'
export type SandboxObjectKind = 'entity' | 'literal'

export type SandboxTriple = {
  id: string
  subjectId: string
  subjectLabel: string
  predicateId: string
  predicateLabel: string
  objectValue: string
  objectLabel: string
  objectKind: SandboxObjectKind
  derived?: boolean
  rdfSubject: string
  rdfPredicate: string
  rdfObject: string
}

export type PrdSegmentRole = 'class' | 'objectProperty' | 'dataProperty' | 'rule'

export type PrdAnnotatedSegment = {
  id: string
  text: string
  role: PrdSegmentRole
  roleLabel: string
  explanation: string
  mappedTarget: string
}

export const PRD_ORDER_STORY_SEGMENTS: readonly PrdAnnotatedSegment[] = [
  {
    id: 'seg-member',
    text: '黑金会员王敏（#M-018）',
    role: 'class',
    roleLabel: '实体类 / 个体',
    explanation: '“黑金会员”是概念类，“王敏 #M-018”是该类下的唯一稳定个体，不靠姓名字符串区分。',
    mappedTarget: 'retail:BlackGoldMember · retail:member/M-018',
  },
  {
    id: 'seg-store',
    text: '在静安旗舰店（#S-01）',
    role: 'objectProperty',
    roleLabel: '对象关系',
    explanation:
      '订单通过“下单门店”对象关系指向门店圆节点，从而可继续串联“门店 → 负责店长 → 阿杰/Jie”。',
    mappedTarget: 'retail:orderAtStore → retail:store/S-01',
  },
  {
    id: 'seg-items',
    text: '同时下单杨枝甘露与茉莉奶绿两杯饮品',
    role: 'objectProperty',
    roleLabel: '事件实体化',
    explanation: '“购买了”不能直接连会员和商品，必须抽象出门店订单事件 #SO-101，才能挂载多杯商品。',
    mappedTarget: 'retail:StoreOrder (#SO-101) — retail:includesProduct → SKU-Y01 / SKU-M02',
  },
  {
    id: 'seg-amount',
    text: '实付 36.00 元且外卖超时 25 分钟',
    role: 'dataProperty',
    roleLabel: '数值属性',
    explanation:
      '实付金额（decimal）与超时分钟（integer）是挂载在订单 #SO-101 上的方盒子数值属性，受 SHACL 非负约束保护。',
    mappedTarget: 'retail:paidAmount (36.00) · retail:overtimeMinutes (25)',
  },
  {
    id: 'seg-rule',
    text: '触发华东区高优超时客诉赔付并自动标为高流失风险待挽回',
    role: 'rule',
    roleLabel: '规则推导',
    explanation:
      '客诉 #CP-301 关联订单 #SO-101 后，规则自动推导 #M-018 属于 ChurnRiskMember，无需人工打标。',
    mappedTarget: 'R-retail-churn-risk → retail:ChurnRiskMember',
  },
] as const

export const REIFIED_SO101_TRIPLES: readonly SandboxTriple[] = [
  {
    id: 'so101-ordered-by',
    subjectId: 'order/SO-101',
    subjectLabel: '门店订单 #SO-101',
    predicateId: 'orderedBy',
    predicateLabel: '下单会员',
    objectValue: 'member/M-018',
    objectLabel: '王敏 #M-018',
    objectKind: 'entity',
    rdfSubject: `${RETAIL_NS}order/SO-101`,
    rdfPredicate: `${RETAIL_NS}orderedBy`,
    rdfObject: `<${RETAIL_NS}member/M-018>`,
  },
  {
    id: 'so101-at-store',
    subjectId: 'order/SO-101',
    subjectLabel: '门店订单 #SO-101',
    predicateId: 'orderAtStore',
    predicateLabel: '下单门店',
    objectValue: 'store/S-01',
    objectLabel: '静安旗舰店 #S-01',
    objectKind: 'entity',
    rdfSubject: `${RETAIL_NS}order/SO-101`,
    rdfPredicate: `${RETAIL_NS}orderAtStore`,
    rdfObject: `<${RETAIL_NS}store/S-01>`,
  },
  {
    id: 'so101-product-1',
    subjectId: 'order/SO-101',
    subjectLabel: '门店订单 #SO-101',
    predicateId: 'includesProduct',
    predicateLabel: '包含商品',
    objectValue: 'product/SKU-Y01',
    objectLabel: '杨枝甘露 #SKU-Y01',
    objectKind: 'entity',
    rdfSubject: `${RETAIL_NS}order/SO-101`,
    rdfPredicate: `${RETAIL_NS}includesProduct`,
    rdfObject: `<${RETAIL_NS}product/SKU-Y01>`,
  },
  {
    id: 'so101-product-2',
    subjectId: 'order/SO-101',
    subjectLabel: '门店订单 #SO-101',
    predicateId: 'includesProduct',
    predicateLabel: '包含商品',
    objectValue: 'product/SKU-M02',
    objectLabel: '茉莉奶绿 #SKU-M02',
    objectKind: 'entity',
    rdfSubject: `${RETAIL_NS}order/SO-101`,
    rdfPredicate: `${RETAIL_NS}includesProduct`,
    rdfObject: `<${RETAIL_NS}product/SKU-M02>`,
  },
  {
    id: 'so101-paid-amount',
    subjectId: 'order/SO-101',
    subjectLabel: '门店订单 #SO-101',
    predicateId: 'paidAmount',
    predicateLabel: '实付金额（元）',
    objectValue: '36.00',
    objectLabel: '36.00 元',
    objectKind: 'literal',
    rdfSubject: `${RETAIL_NS}order/SO-101`,
    rdfPredicate: `${RETAIL_NS}paidAmount`,
    rdfObject: '"36.00"^^<http://www.w3.org/2001/XMLSchema#decimal>',
  },
] as const

export const DERIVED_CHURN_TRIPLE: SandboxTriple = {
  id: 'derived-m018-churn',
  subjectId: 'member/M-018',
  subjectLabel: '王敏 #M-018',
  predicateId: 'derivedRisk',
  predicateLabel: '规则推导标签',
  objectValue: 'ChurnRiskMember',
  objectLabel: '高流失风险待挽回会员',
  objectKind: 'entity',
  derived: true,
  rdfSubject: `${RETAIL_NS}member/M-018`,
  rdfPredicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
  rdfObject: `<${RETAIL_NS}ChurnRiskMember>`,
}

export const INITIAL_STEP_TRIPLE: Record<FoundationMicroStepId, SandboxTriple> = {
  'step-01': REIFIED_SO101_TRIPLES[4]!,
  'step-02': {
    id: 'step02-m018-name',
    subjectId: 'member/M-018',
    subjectLabel: '王敏 #M-018',
    predicateId: 'displayName',
    predicateLabel: '显示名称',
    objectValue: '王敏',
    objectLabel: '"王敏" (黑金)',
    objectKind: 'literal',
    rdfSubject: `${RETAIL_NS}member/M-018`,
    rdfPredicate: `${RETAIL_NS}displayName`,
    rdfObject: '"王敏"@zh',
  },
  'step-03': REIFIED_SO101_TRIPLES[1]!,
  'step-04': {
    id: 'step04-m018-type',
    subjectId: 'member/M-018',
    subjectLabel: '王敏 #M-018',
    predicateId: 'rdfType',
    predicateLabel: '属于类型',
    objectValue: 'BlackGoldMember',
    objectLabel: '黑金会员（类）',
    objectKind: 'entity',
    rdfSubject: `${RETAIL_NS}member/M-018`,
    rdfPredicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
    rdfObject: `<${RETAIL_NS}BlackGoldMember>`,
  },
  'step-05': REIFIED_SO101_TRIPLES[0]!,
  'step-06': DERIVED_CHURN_TRIPLE,
}
