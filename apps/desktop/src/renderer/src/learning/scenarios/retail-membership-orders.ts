import type {
  QualityFr505PatternDTO,
  QualityFr505TripleDTO,
  QualityRuleTestRequestDTO,
  QualityRuleTestSampleRuleDTO,
} from '@ontolearn/contracts'

export const RETAIL_NS = 'urn:ontolearn:retail:'
export const RETAIL_PREFIX = 'retail:'

export type RetailDatasetScale = 'micro10' | 'stress80'
export type RetailSourceTableId = 'members' | 'stores_staff' | 'orders' | 'complaints'
export type FoundationMicroStepId =
  'step-01' | 'step-02' | 'step-03' | 'step-04' | 'step-05' | 'step-06'

export type RetailVocabularyItem = {
  iri: string
  compactIri: string
  zhLabel: string
  kind: 'class' | 'objectProperty' | 'dataProperty' | 'individual'
  domain?: string
  range?: string
  datatype?: 'string' | 'zhText' | 'decimal' | 'integer' | 'boolean'
  plainHint: string
}

export type RetailAnomalyTag =
  | 'missing_store'
  | 'negative_amount'
  | 'dangling_manager'
  | 'churn_target'
  | 'homonym'
  | 'renamed_staff'

export type RetailTableRow = {
  table: RetailSourceTableId
  rowId: string
  cells: Record<string, string | number | null>
  anomalyTag?: RetailAnomalyTag
}

export type FoundationMicroStep = {
  id: FoundationMicroStepId
  num: string
  title: string
  conceptSummary: string
  recommendedMode: 'excel' | 'clinic'
  defaultTable: RetailSourceTableId
  targetOutcome: string
}

export type RetailSourceTableMeta = {
  id: RetailSourceTableId
  title: string
  subtitle: string
  columns: readonly { key: string; label: string }[]
}

export type RetailSimulationSample = {
  scale: RetailDatasetScale
  request: QualityRuleTestRequestDTO
  anomalySummary: {
    totalRows: number
    missingStoreCount: number
    negativeAmountCount: number
    danglingManagerCount: number
    churnTargetCount: number
    missingStoreIds: readonly string[]
    negativeAmountIds: readonly string[]
    danglingManagerStoreIds: readonly string[]
    churnTargetMemberIds: readonly string[]
  }
}

export const RETAIL_SOURCE_TABLES: readonly RetailSourceTableMeta[] = [
  {
    id: 'members',
    title: 'members · 小程序会员档案表',
    subtitle: '包含同名会员识别、会员等级与注册渠道',
    columns: [
      { key: 'memberId', label: '会员编号' },
      { key: 'displayName', label: '显示名称' },
      { key: 'tier', label: '会员等级' },
      { key: 'channel', label: '注册渠道' },
      { key: 'phoneSuffix', label: '手机尾号' },
    ],
  },
  {
    id: 'stores_staff',
    title: 'stores_staff · 门店与店长台账',
    subtitle: '包含华东区域、运营模式、店长工号与花名更迭',
    columns: [
      { key: 'storeId', label: '门店编号' },
      { key: 'storeName', label: '门店名称' },
      { key: 'regionCode', label: '所属大区' },
      { key: 'storeMode', label: '经营模式' },
      { key: 'managerId', label: '店长工号' },
      { key: 'managerName', label: '店长显示名' },
      { key: 'formerName', label: '曾用花名' },
    ],
  },
  {
    id: 'orders',
    title: 'orders · 全渠道订单流水',
    subtitle: '包含多杯同单事件实体、实付金额与超时分钟数',
    columns: [
      { key: 'orderId', label: '订单编号' },
      { key: 'memberId', label: '下单会员' },
      { key: 'storeId', label: '下单门店' },
      { key: 'itemsSummary', label: '商品明细' },
      { key: 'paidAmount', label: '实付金额' },
      { key: 'overtimeMinutes', label: '超时分钟' },
      { key: 'channel', label: '履约渠道' },
    ],
  },
  {
    id: 'complaints',
    title: 'complaints · 超时客诉与赔付单',
    subtitle: '记录超时客诉级别、赔付动作与回访状态',
    columns: [
      { key: 'complaintId', label: '客诉单号' },
      { key: 'orderId', label: '关联订单' },
      { key: 'memberId', label: '会员编号' },
      { key: 'severity', label: '客诉等级' },
      { key: 'compensationStatus', label: '赔付状态' },
      { key: 'followUpStatus', label: '回访状态' },
    ],
  },
] as const

export const FOUNDATION_MICRO_STEPS: readonly FoundationMicroStep[] = [
  {
    id: 'step-01',
    num: 'Step 01',
    title: '万物皆三元组（S–P–O 原子事实）',
    conceptSummary: '把 Excel 一行宽表拆成 [主语] — [谓语] → [宾语] 积木，新增字段无需改动整张表。',
    recommendedMode: 'excel',
    defaultTable: 'orders',
    targetOutcome: '拆出订单 #SO-101 的实付金额或下单门店三元组',
  },
  {
    id: 'step-02',
    num: 'Step 02',
    title: '唯一身份 ID vs 显示名称（IRI vs Label）',
    conceptSummary:
      '区分“两个王敏（#M-018 vs #M-209）”与“阿杰改名 Jie（#EMP-07）”：名称可变，ID 唯一稳定。',
    recommendedMode: 'excel',
    defaultTable: 'members',
    targetOutcome: '点击同名王敏行完成稳定身份对照',
  },
  {
    id: 'step-03',
    num: 'Step 03',
    title: '对象关系 vs 数值属性（圆节点 vs 方字面量）',
    conceptSummary:
      '下单门店指向“静安旗舰店”（可继续牵出店长的圆节点），实付金额 36.00 是到此为止的方盒子。',
    recommendedMode: 'excel',
    defaultTable: 'orders',
    targetOutcome: '验证对象属性必须连圆节点、数值属性填字面量',
  },
  {
    id: 'step-04',
    num: 'Step 04',
    title: '类（模具）vs 个体（实例）与上下位层级',
    conceptSummary:
      '“黑金会员”是概念模具，“王敏 #M-018”是具体个体；黑金会员 ⊂ 注册会员会自动继承规则。',
    recommendedMode: 'excel',
    defaultTable: 'members',
    targetOutcome: '为个体 #M-018 建立所属类声明',
  },
  {
    id: 'step-05',
    num: 'Step 05',
    title: '关系方向性与事件实体化（坏模型诊所）',
    conceptSummary:
      '不能只连“王敏 —购买了→ 杨枝甘露”，必须重构独立订单事件 #SO-101 挂载金额、时间与多杯明细。',
    recommendedMode: 'clinic',
    defaultTable: 'orders',
    targetOutcome: '一键重构 #SO-101 事件实体模型并带入正式草稿',
  },
  {
    id: 'step-06',
    num: 'Step 06',
    title: '显式断言 vs 规则推导 & 开放世界 SHACL 体检',
    conceptSummary:
      '人工只录事实，“高流失风险待挽回会员”由规则自动推导；漏填在开放世界不自动报错，靠 SHACL 拦截。',
    recommendedMode: 'excel',
    defaultTable: 'complaints',
    targetOutcome: '观察推导虚线边并理解 80 行压力集体检逻辑',
  },
] as const

export const RETAIL_VOCABULARY: readonly RetailVocabularyItem[] = [
  {
    iri: `${RETAIL_NS}Member`,
    compactIri: 'retail:Member',
    zhLabel: '注册会员（类）',
    kind: 'class',
    plainHint: '茶饮全渠道所有已注册消费者的上位概念模具。',
  },
  {
    iri: `${RETAIL_NS}BlackGoldMember`,
    compactIri: 'retail:BlackGoldMember',
    zhLabel: '黑金会员（子类）',
    kind: 'class',
    plainHint: '注册会员的子类，享有高优超时赔付保障。',
  },
  {
    iri: `${RETAIL_NS}RegularMember`,
    compactIri: 'retail:RegularMember',
    zhLabel: '普通会员（子类）',
    kind: 'class',
    plainHint: '注册会员的常规等级子类。',
  },
  {
    iri: `${RETAIL_NS}Store`,
    compactIri: 'retail:Store',
    zhLabel: '茶饮门店（类）',
    kind: 'class',
    plainHint: '线下制作与履约订单的实体门店。',
  },
  {
    iri: `${RETAIL_NS}Staff`,
    compactIri: 'retail:Staff',
    zhLabel: '门店员工/店长（类）',
    kind: 'class',
    plainHint: '负责门店日常履约与客诉处理的店长或店员。',
  },
  {
    iri: `${RETAIL_NS}StoreOrder`,
    compactIri: 'retail:StoreOrder',
    zhLabel: '门店订单事件（类）',
    kind: 'class',
    plainHint: '将一次购买动作实体化为独立订单节点，用于挂载实付、门店与多杯商品。',
  },
  {
    iri: `${RETAIL_NS}Product`,
    compactIri: 'retail:Product',
    zhLabel: '茶饮商品（类）',
    kind: 'class',
    plainHint: '可被同一订单多次包含的饮品 SKU。',
  },
  {
    iri: `${RETAIL_NS}ComplaintTicket`,
    compactIri: 'retail:ComplaintTicket',
    zhLabel: '超时客诉单（类）',
    kind: 'class',
    plainHint: '订单超时后触发的客诉与免单券赔付工单。',
  },
  {
    iri: `${RETAIL_NS}ChurnRiskMember`,
    compactIri: 'retail:ChurnRiskMember',
    zhLabel: '高流失风险待挽回会员（推导类）',
    kind: 'class',
    plainHint: '不手工录入，由规则根据“黑金会员 + 华东门店 + 超时客诉”自动推导打标。',
  },
  {
    iri: `${RETAIL_NS}orderedBy`,
    compactIri: 'retail:orderedBy',
    zhLabel: '下单会员',
    kind: 'objectProperty',
    domain: `${RETAIL_NS}StoreOrder`,
    range: `${RETAIL_NS}Member`,
    plainHint: '将门店订单关联到下单会员个体（对象关系，只能连圆节点）。',
  },
  {
    iri: `${RETAIL_NS}placedOrder`,
    compactIri: 'retail:placedOrder',
    zhLabel: '发起订单',
    kind: 'objectProperty',
    domain: `${RETAIL_NS}Member`,
    range: `${RETAIL_NS}StoreOrder`,
    plainHint: '从会员出发指向门店订单事件节点。',
  },
  {
    iri: `${RETAIL_NS}orderAtStore`,
    compactIri: 'retail:orderAtStore',
    zhLabel: '下单门店',
    kind: 'objectProperty',
    domain: `${RETAIL_NS}StoreOrder`,
    range: `${RETAIL_NS}Store`,
    plainHint: '将订单关联到履约门店圆节点，从而可继续串联店长。',
  },
  {
    iri: `${RETAIL_NS}managedBy`,
    compactIri: 'retail:managedBy',
    zhLabel: '负责店长',
    kind: 'objectProperty',
    domain: `${RETAIL_NS}Store`,
    range: `${RETAIL_NS}Staff`,
    plainHint: '门店对应的负责店长员工个体。',
  },
  {
    iri: `${RETAIL_NS}includesProduct`,
    compactIri: 'retail:includesProduct',
    zhLabel: '包含商品',
    kind: 'objectProperty',
    domain: `${RETAIL_NS}StoreOrder`,
    range: `${RETAIL_NS}Product`,
    plainHint: '支持单笔订单挂载多杯不同茶饮商品。',
  },
  {
    iri: `${RETAIL_NS}complaintForOrder`,
    compactIri: 'retail:complaintForOrder',
    zhLabel: '关联订单',
    kind: 'objectProperty',
    domain: `${RETAIL_NS}ComplaintTicket`,
    range: `${RETAIL_NS}StoreOrder`,
    plainHint: '把超时客诉单精准挂载到具体哪一笔订单。',
  },
  {
    iri: `${RETAIL_NS}displayName`,
    compactIri: 'retail:displayName',
    zhLabel: '显示名称',
    kind: 'dataProperty',
    datatype: 'zhText',
    plainHint: '人物或门店的中文展示姓名，允许重名或修改，不充当主键。',
  },
  {
    iri: `${RETAIL_NS}memberTier`,
    compactIri: 'retail:memberTier',
    zhLabel: '会员等级文本',
    kind: 'dataProperty',
    datatype: 'zhText',
    plainHint: '记录“黑金会员”或“普通会员”业务标签。',
  },
  {
    iri: `${RETAIL_NS}regionCode`,
    compactIri: 'retail:regionCode',
    zhLabel: '所属大区',
    kind: 'dataProperty',
    datatype: 'zhText',
    plainHint: '如“华东区”“华南区”，是规则推导的重要地理条件。',
  },
  {
    iri: `${RETAIL_NS}paidAmount`,
    compactIri: 'retail:paidAmount',
    zhLabel: '实付金额（元）',
    kind: 'dataProperty',
    datatype: 'decimal',
    plainHint: '订单实际支付金额（小数），SHACL 约束要求 >= 0。',
  },
  {
    iri: `${RETAIL_NS}overtimeMinutes`,
    compactIri: 'retail:overtimeMinutes',
    zhLabel: '超时分钟数',
    kind: 'dataProperty',
    datatype: 'integer',
    plainHint: '订单履约超出的整数分钟数。',
  },
  {
    iri: `${RETAIL_NS}channel`,
    compactIri: 'retail:channel',
    zhLabel: '下单渠道',
    kind: 'dataProperty',
    datatype: 'zhText',
    plainHint: '如“小程序外卖”或“门店自提”。',
  },
  {
    iri: `${RETAIL_NS}compensationStatus`,
    compactIri: 'retail:compensationStatus',
    zhLabel: '赔付状态',
    kind: 'dataProperty',
    datatype: 'zhText',
    plainHint: '仅允许标准业务态：已赔付 / 处理中 / 待回访。',
  },
  {
    iri: `${RETAIL_NS}isCompensated`,
    compactIri: 'retail:isCompensated',
    zhLabel: '是否已赔付',
    kind: 'dataProperty',
    datatype: 'boolean',
    plainHint: '布尔标记（true / false）。',
  },
  {
    iri: `${RETAIL_NS}member/M-018`,
    compactIri: 'retail:member/M-018',
    zhLabel: '王敏 #M-018（黑金会员）',
    kind: 'individual',
    plainHint: '黑金会员王敏（尾号 8818），与 #M-209 同名但身份 IRI 独立。',
  },
  {
    iri: `${RETAIL_NS}member/M-209`,
    compactIri: 'retail:member/M-209',
    zhLabel: '王敏 #M-209（普通会员）',
    kind: 'individual',
    plainHint: '普通会员王敏（尾号 4309），用于演示同名不混淆。',
  },
  {
    iri: `${RETAIL_NS}member/M-031`,
    compactIri: 'retail:member/M-031',
    zhLabel: '陈晨 #M-031（黑金会员）',
    kind: 'individual',
    plainHint: '华东区黑金会员个体。',
  },
  {
    iri: `${RETAIL_NS}member/M-042`,
    compactIri: 'retail:member/M-042',
    zhLabel: '林悦 #M-042（黑金会员）',
    kind: 'individual',
    plainHint: '华东区黑金会员个体。',
  },
  {
    iri: `${RETAIL_NS}member/M-056`,
    compactIri: 'retail:member/M-056',
    zhLabel: '周航 #M-056（黑金会员）',
    kind: 'individual',
    plainHint: '华东区黑金会员个体。',
  },
  {
    iri: `${RETAIL_NS}store/S-01`,
    compactIri: 'retail:store/S-01',
    zhLabel: '静安旗舰店 #S-01',
    kind: 'individual',
    plainHint: '华东区直营门店，由店长 #EMP-07 负责。',
  },
  {
    iri: `${RETAIL_NS}store/S-02`,
    compactIri: 'retail:store/S-02',
    zhLabel: '徐汇美罗店 #S-02',
    kind: 'individual',
    plainHint: '华东区直营门店。',
  },
  {
    iri: `${RETAIL_NS}staff/EMP-07`,
    compactIri: 'retail:staff/EMP-07',
    zhLabel: '店长 Jie（原阿杰）#EMP-07',
    kind: 'individual',
    plainHint: '花名由“阿杰”改为“Jie”，但稳定 IRI 保持不变。',
  },
  {
    iri: `${RETAIL_NS}order/SO-101`,
    compactIri: 'retail:order/SO-101',
    zhLabel: '门店订单 #SO-101',
    kind: 'individual',
    plainHint: '王敏 #M-018 在静安旗舰店下单的事件实体（实付 36.00，超时 25 分钟）。',
  },
  {
    iri: `${RETAIL_NS}product/SKU-Y01`,
    compactIri: 'retail:product/SKU-Y01',
    zhLabel: '杨枝甘露 #SKU-Y01',
    kind: 'individual',
    plainHint: '门店热销果茶单品。',
  },
  {
    iri: `${RETAIL_NS}product/SKU-M02`,
    compactIri: 'retail:product/SKU-M02',
    zhLabel: '茉莉奶绿 #SKU-M02',
    kind: 'individual',
    plainHint: '门店经典鲜奶茶单品。',
  },
  {
    iri: `${RETAIL_NS}complaint/CP-301`,
    compactIri: 'retail:complaint/CP-301',
    zhLabel: '超时客诉单 #CP-301',
    kind: 'individual',
    plainHint: '关联 #SO-101 订单，已发放免单券赔付，处于待回访状态。',
  },
] as const

/** Exact 10-row micro sandbox dataset (3 members + 2 stores_staff + 3 orders + 2 complaints). */
export const RETAIL_MICRO_10_ROWS: readonly RetailTableRow[] = [
  {
    table: 'members',
    rowId: 'M-018',
    anomalyTag: 'homonym',
    cells: {
      memberId: '#M-018',
      displayName: '王敏',
      tier: '黑金会员',
      channel: '小程序点单',
      phoneSuffix: '8818',
    },
  },
  {
    table: 'members',
    rowId: 'M-209',
    anomalyTag: 'homonym',
    cells: {
      memberId: '#M-209',
      displayName: '王敏',
      tier: '普通会员',
      channel: '门店扫码',
      phoneSuffix: '4309',
    },
  },
  {
    table: 'members',
    rowId: 'M-031',
    cells: {
      memberId: '#M-031',
      displayName: '陈晨',
      tier: '黑金会员',
      channel: '企业团购',
      phoneSuffix: '6621',
    },
  },
  {
    table: 'stores_staff',
    rowId: 'S-01',
    anomalyTag: 'renamed_staff',
    cells: {
      storeId: '#S-01',
      storeName: '静安旗舰店',
      regionCode: '华东区',
      storeMode: '直营',
      managerId: '#EMP-07',
      managerName: 'Jie',
      formerName: '阿杰',
    },
  },
  {
    table: 'stores_staff',
    rowId: 'S-02',
    cells: {
      storeId: '#S-02',
      storeName: '徐汇美罗店',
      regionCode: '华东区',
      storeMode: '直营',
      managerId: '#EMP-12',
      managerName: '林琳',
      formerName: '无',
    },
  },
  {
    table: 'orders',
    rowId: 'SO-101',
    cells: {
      orderId: '#SO-101',
      memberId: '#M-018',
      storeId: '#S-01',
      itemsSummary: '杨枝甘露 + 茉莉奶绿',
      paidAmount: 36.0,
      overtimeMinutes: 25,
      channel: '小程序外卖',
    },
  },
  {
    table: 'orders',
    rowId: 'SO-102',
    cells: {
      orderId: '#SO-102',
      memberId: '#M-209',
      storeId: '#S-02',
      itemsSummary: '生椰拿铁',
      paidAmount: 19.0,
      overtimeMinutes: 0,
      channel: '门店自提',
    },
  },
  {
    table: 'orders',
    rowId: 'SO-103',
    cells: {
      orderId: '#SO-103',
      memberId: '#M-031',
      storeId: '#S-01',
      itemsSummary: '芝士葡萄 + 桂花乌龙',
      paidAmount: 42.0,
      overtimeMinutes: 12,
      channel: '门店自提',
    },
  },
  {
    table: 'complaints',
    rowId: 'CP-301',
    cells: {
      complaintId: '#CP-301',
      orderId: '#SO-101',
      memberId: '#M-018',
      severity: '高优超时赔付',
      compensationStatus: '已赔付',
      followUpStatus: '待回访',
    },
  },
  {
    table: 'complaints',
    rowId: 'CP-302',
    cells: {
      complaintId: '#CP-302',
      orderId: '#SO-103',
      memberId: '#M-031',
      severity: '常规提醒',
      compensationStatus: '处理中',
      followUpStatus: '待回访',
    },
  },
] as const

const SURNAMES = ['王', '李', '张', '陈', '林', '周', '赵', '黄', '吴', '徐'] as const
const GIVEN_NAMES = ['敏', '晨', '悦', '航', '宇', '婷', '杰', '静', '涛', '雪'] as const
const CHANNELS = ['小程序外卖', '门店自提', '企微社群券'] as const
const DRINKS = [
  '杨枝甘露 + 茉莉奶绿',
  '生椰拿铁',
  '芝士葡萄 + 桂花乌龙',
  '满杯西柚',
  '栀子绿茶',
] as const

function buildStress80Rows(): readonly RetailTableRow[] {
  const rows: RetailTableRow[] = []

  // 1. 20 members (4 exact churn targets: M-018, M-031, M-042, M-056; plus M-209 homonym)
  const churnTargets = new Set(['M-018', 'M-031', 'M-042', 'M-056'])
  const presetMembers: Array<{
    id: string
    name: string
    tier: string
    channel: string
    phone: string
    tag?: RetailAnomalyTag
  }> = [
    {
      id: 'M-018',
      name: '王敏',
      tier: '黑金会员',
      channel: '小程序点单',
      phone: '8818',
      tag: 'churn_target',
    },
    {
      id: 'M-209',
      name: '王敏',
      tier: '普通会员',
      channel: '门店扫码',
      phone: '4309',
      tag: 'homonym',
    },
    {
      id: 'M-031',
      name: '陈晨',
      tier: '黑金会员',
      channel: '企业团购',
      phone: '6621',
      tag: 'churn_target',
    },
    {
      id: 'M-042',
      name: '林悦',
      tier: '黑金会员',
      channel: '小程序点单',
      phone: '7742',
      tag: 'churn_target',
    },
    {
      id: 'M-056',
      name: '周航',
      tier: '黑金会员',
      channel: '小程序点单',
      phone: '9056',
      tag: 'churn_target',
    },
  ]
  for (const m of presetMembers) {
    rows.push({
      table: 'members',
      rowId: m.id,
      anomalyTag: m.tag,
      cells: {
        memberId: `#${m.id}`,
        displayName: m.name,
        tier: m.tier,
        channel: m.channel,
        phoneSuffix: m.phone,
      },
    })
  }
  for (let i = 5; i < 20; i++) {
    const num = 100 + i
    const id = `M-${num}`
    const name = `${SURNAMES[i % SURNAMES.length]}${GIVEN_NAMES[(i * 3) % GIVEN_NAMES.length]}`
    rows.push({
      table: 'members',
      rowId: id,
      cells: {
        memberId: `#${id}`,
        displayName: name,
        tier: i === 7 ? '黑金会员' : '普通会员',
        channel: i % 2 === 0 ? '小程序点单' : '门店扫码',
        phoneSuffix: String(3100 + i * 17),
      },
    })
  }

  // 2. 12 stores_staff (exact 2 dangling_manager rows: S-09 and S-11 -> #EMP-999)
  const storeCities = [
    ['S-01', '静安旗舰店', '华东区', '直营', 'EMP-07', 'Jie', '阿杰', 'renamed_staff'],
    ['S-02', '徐汇美罗店', '华东区', '直营', 'EMP-12', '林琳', '无', undefined],
    ['S-03', '杭州湖滨银泰店', '华东区', '直营', 'EMP-15', '许诺', '无', undefined],
    ['S-04', '南京新街口店', '华东区', '加盟', 'EMP-18', '何安', '无', undefined],
    ['S-05', '深圳海岸城店', '华南区', '直营', 'EMP-21', '苏青', '无', undefined],
    ['S-06', '广州天河城店', '华南区', '直营', 'EMP-24', '陆鸣', '无', undefined],
    ['S-07', '北京三里屯店', '华北区', '直营', 'EMP-27', '沈岚', '无', undefined],
    ['S-08', '成都太古里店', '西南区', '直营', 'EMP-30', '唐可', '无', undefined],
    ['S-09', '苏州中心店', '华东区', '加盟', 'EMP-999', '未关联', '无', 'dangling_manager'],
    ['S-10', '宁波天一广场店', '华东区', '加盟', 'EMP-33', '韩冬', '无', undefined],
    ['S-11', '无锡恒隆店', '华东区', '加盟', 'EMP-999', '未关联', '无', 'dangling_manager'],
    ['S-12', '武汉楚河汉街店', '华中区', '直营', 'EMP-36', '宋一', '无', undefined],
  ] as const
  for (const [id, name, region, mode, empId, empName, former, tag] of storeCities) {
    rows.push({
      table: 'stores_staff',
      rowId: id,
      ...(tag ? { anomalyTag: tag } : {}),
      cells: {
        storeId: `#${id}`,
        storeName: name,
        regionCode: region,
        storeMode: mode,
        managerId: `#${empId}`,
        managerName: empName,
        formerName: former,
      },
    })
  }

  // 3. 36 orders (exact 3 missing_store rows, exact 2 negative_amount rows, 4 churn-linked East China orders)
  const missingStoreIdx = new Set([4, 19, 33])
  const negativeAmountIdx = new Set([8, 25])
  const churnOrderSetup: Array<{
    idx: number
    orderId: string
    memberId: string
    storeId: string
  }> = [
    { idx: 0, orderId: 'SO-101', memberId: 'M-018', storeId: 'S-01' },
    { idx: 1, orderId: 'SO-102', memberId: 'M-031', storeId: 'S-02' },
    { idx: 2, orderId: 'SO-103', memberId: 'M-042', storeId: 'S-03' },
    { idx: 3, orderId: 'SO-104', memberId: 'M-056', storeId: 'S-01' },
  ]
  const churnByIdx = new Map(churnOrderSetup.map((item) => [item.idx, item]))

  for (let i = 0; i < 36; i++) {
    const preset = churnByIdx.get(i)
    const orderId = preset ? preset.orderId : `SO-${200 + i}`
    const memberId = preset ? preset.memberId : i === 5 ? 'M-209' : `M-${105 + ((i - 4) % 15)}`
    const isMissingStore = missingStoreIdx.has(i)
    const isNegative = negativeAmountIdx.has(i)
    const storeId = preset
      ? preset.storeId
      : isMissingStore
        ? null
        : `S-${String(5 + (i % 7)).padStart(2, '0')}`
    const paidAmount = isNegative ? (i === 8 ? -12.0 : -18.5) : 18 + (i % 5) * 6
    const overtimeMinutes = preset ? 25 + i * 3 : i % 6 === 0 ? 15 : 0
    const anomalyTag: RetailAnomalyTag | undefined = isMissingStore
      ? 'missing_store'
      : isNegative
        ? 'negative_amount'
        : undefined
    rows.push({
      table: 'orders',
      rowId: orderId,
      ...(anomalyTag ? { anomalyTag } : {}),
      cells: {
        orderId: `#${orderId}`,
        memberId: `#${memberId}`,
        storeId: storeId ? `#${storeId}` : null,
        itemsSummary: DRINKS[i % DRINKS.length],
        paidAmount,
        overtimeMinutes,
        channel: CHANNELS[i % CHANNELS.length],
      },
    })
  }

  // 4. 12 complaints (first 4 link directly to the 4 churn-target black-gold orders; rest link to non-East-China/regular orders)
  for (let i = 0; i < 12; i++) {
    const complaintId = `CP-${301 + i}`
    const churn = churnOrderSetup[i]
    const orderId = churn ? churn.orderId : `SO-${205 + i}`
    const memberId = churn ? churn.memberId : `M-${105 + (i % 10)}`
    const isChurn = churn !== undefined && churnTargets.has(churn.memberId)
    rows.push({
      table: 'complaints',
      rowId: complaintId,
      ...(isChurn ? { anomalyTag: 'churn_target' } : {}),
      cells: {
        complaintId: `#${complaintId}`,
        orderId: `#${orderId}`,
        memberId: `#${memberId}`,
        severity: isChurn ? '高优超时赔付' : '常规咨询',
        compensationStatus: i % 3 === 0 ? '已赔付' : '处理中',
        followUpStatus: '待回访',
      },
    })
  }

  return rows
}

export const RETAIL_STRESS_80_ROWS: readonly RetailTableRow[] = buildStress80Rows()

export function getRetailRows(scale: RetailDatasetScale): readonly RetailTableRow[] {
  return scale === 'micro10' ? RETAIL_MICRO_10_ROWS : RETAIL_STRESS_80_ROWS
}

export function summarizeRetailDataset(scale: RetailDatasetScale) {
  const rows = getRetailRows(scale)
  const missingStoreIds = rows
    .filter((r) => r.table === 'orders' && r.anomalyTag === 'missing_store')
    .map((r) => r.rowId)
  const negativeAmountIds = rows
    .filter((r) => r.table === 'orders' && r.anomalyTag === 'negative_amount')
    .map((r) => r.rowId)
  const danglingManagerStoreIds = rows
    .filter((r) => r.table === 'stores_staff' && r.anomalyTag === 'dangling_manager')
    .map((r) => r.rowId)
  const churnTargetMemberIds = rows
    .filter((r) => r.table === 'members' && r.anomalyTag === 'churn_target')
    .map((r) => r.rowId)

  return {
    totalRows: rows.length,
    missingStoreCount: missingStoreIds.length,
    negativeAmountCount: negativeAmountIds.length,
    danglingManagerCount: danglingManagerStoreIds.length,
    churnTargetCount: churnTargetMemberIds.length,
    missingStoreIds,
    negativeAmountIds,
    danglingManagerStoreIds,
    churnTargetMemberIds,
  }
}

const RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
const RDFS_SUBCLASS = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
const OWL_CLASS = 'http://www.w3.org/2002/07/owl#Class'
const OWL_OBJECT_PROP = 'http://www.w3.org/2002/07/owl#ObjectProperty'
const OWL_DATA_PROP = 'http://www.w3.org/2002/07/owl#DatatypeProperty'

function iriRef(local: string): string {
  return `<${RETAIL_NS}${local}>`
}

function escapeN3String(text: string): string {
  return text
    .replaceAll('\\', '\\\\')
    .replaceAll('"', '\\"')
    .replaceAll('\n', '\\n')
    .replaceAll('\r', '\\r')
}

export function buildRetailQualitySample(scale: RetailDatasetScale): RetailSimulationSample {
  const rows = getRetailRows(scale)
  const summary = summarizeRetailDataset(scale)

  const ontologyTriples: QualityFr505TripleDTO[] = [
    [`${RETAIL_NS}Member`, RDF_TYPE, `<${OWL_CLASS}>`],
    [`${RETAIL_NS}BlackGoldMember`, RDF_TYPE, `<${OWL_CLASS}>`],
    [`${RETAIL_NS}BlackGoldMember`, RDFS_SUBCLASS, iriRef('Member')],
    [`${RETAIL_NS}ChurnRiskMember`, RDF_TYPE, `<${OWL_CLASS}>`],
    [`${RETAIL_NS}orderedBy`, RDF_TYPE, `<${OWL_OBJECT_PROP}>`],
    [`${RETAIL_NS}orderAtStore`, RDF_TYPE, `<${OWL_OBJECT_PROP}>`],
    [`${RETAIL_NS}complaintForOrder`, RDF_TYPE, `<${OWL_OBJECT_PROP}>`],
    [`${RETAIL_NS}memberTier`, RDF_TYPE, `<${OWL_DATA_PROP}>`],
    [`${RETAIL_NS}regionCode`, RDF_TYPE, `<${OWL_DATA_PROP}>`],
  ]

  const complainedOrderIds = new Set(
    rows
      .filter((r) => r.table === 'complaints' && typeof r.cells.orderId === 'string')
      .map((r) => String(r.cells.orderId).replace(/^#/, '')),
  )
  const referencedMemberIds = new Set(
    rows
      .filter(
        (r) =>
          r.table === 'orders' &&
          complainedOrderIds.has(r.rowId) &&
          typeof r.cells.memberId === 'string',
      )
      .map((r) => String(r.cells.memberId).replace(/^#/, '')),
  )
  const referencedStoreIds = new Set(
    rows
      .filter(
        (r) =>
          r.table === 'orders' &&
          complainedOrderIds.has(r.rowId) &&
          typeof r.cells.storeId === 'string',
      )
      .map((r) => String(r.cells.storeId).replace(/^#/, '')),
  )

  const inputTriples: QualityFr505TripleDTO[] = []
  for (const row of rows) {
    if (row.table === 'members' && referencedMemberIds.has(row.rowId)) {
      const subject = `${RETAIL_NS}member/${row.rowId}`
      const tier = String(row.cells.tier ?? '普通会员')
      inputTriples.push([subject, `${RETAIL_NS}memberTier`, `"${escapeN3String(tier)}"`])
      if (tier === '黑金会员') {
        inputTriples.push([subject, RDF_TYPE, iriRef('BlackGoldMember')])
      }
    } else if (row.table === 'stores_staff' && referencedStoreIds.has(row.rowId)) {
      const subject = `${RETAIL_NS}store/${row.rowId}`
      if (typeof row.cells.regionCode === 'string') {
        inputTriples.push([
          subject,
          `${RETAIL_NS}regionCode`,
          `"${escapeN3String(row.cells.regionCode)}"`,
        ])
      }
    } else if (row.table === 'orders' && complainedOrderIds.has(row.rowId)) {
      const subject = `${RETAIL_NS}order/${row.rowId}`
      if (typeof row.cells.memberId === 'string') {
        const mId = row.cells.memberId.replace(/^#/, '')
        inputTriples.push([subject, `${RETAIL_NS}orderedBy`, iriRef(`member/${mId}`)])
      }
      if (typeof row.cells.storeId === 'string') {
        const sId = row.cells.storeId.replace(/^#/, '')
        inputTriples.push([subject, `${RETAIL_NS}orderAtStore`, iriRef(`store/${sId}`)])
      }
    } else if (row.table === 'complaints') {
      const subject = `${RETAIL_NS}complaint/${row.rowId}`
      if (typeof row.cells.orderId === 'string') {
        const oId = row.cells.orderId.replace(/^#/, '')
        inputTriples.push([subject, `${RETAIL_NS}complaintForOrder`, iriRef(`order/${oId}`)])
      }
    }
  }

  const conditions: QualityFr505PatternDTO[] = [
    {
      kind: 'property',
      subject: '?complaint',
      path: `${RETAIL_NS}complaintForOrder`,
      object: '?order',
    },
    { kind: 'property', subject: '?order', path: `${RETAIL_NS}orderAtStore`, object: '?store' },
    { kind: 'property', subject: '?store', path: `${RETAIL_NS}regionCode`, object: '"华东区"' },
    { kind: 'property', subject: '?order', path: `${RETAIL_NS}orderedBy`, object: '?member' },
    { kind: 'property', subject: '?member', path: `${RETAIL_NS}memberTier`, object: '"黑金会员"' },
  ]
  const rules: QualityRuleTestSampleRuleDTO[] = [
    {
      id: 'R-retail-churn-risk',
      label: '华东区黑金会员超时客诉推导待挽回名单',
      enabled: true,
      conditions,
      conclusions: [{ kind: 'type', subject: '?member', class: `${RETAIL_NS}ChurnRiskMember` }],
    },
  ]

  // Note: in micro10, both M-018 (#SO-101/#CP-301) and M-031 (#SO-103/#CP-302) satisfy the rule!
  // Wait: let's verify! In micro10:
  // M-018 (黑金会员) -> SO-101 -> S-01 (华东区) <- CP-301
  // M-031 (黑金会员) -> SO-103 -> S-01 (华东区) <- CP-302
  // Both M-018 and M-031 derive ChurnRiskMember in micro10, and in stress80 M-018, M-031, M-042, M-056 derive ChurnRiskMember!
  const expectedMemberIds = scale === 'micro10' ? ['M-018', 'M-031'] : summary.churnTargetMemberIds
  const expectedOutputs: QualityFr505TripleDTO[] = expectedMemberIds.map((memberId) => [
    `${RETAIL_NS}member/${memberId}`,
    RDF_TYPE,
    iriRef('ChurnRiskMember'),
  ])

  return {
    scale,
    request: {
      ontologyTriples,
      inputTriples,
      rules,
      expectedOutputs,
    },
    anomalySummary: summary,
  }
}
