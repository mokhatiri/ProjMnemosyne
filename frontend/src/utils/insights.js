// Pure helpers for explaining and scoring analyst insights.
// Ported from the original single-file console (index1.html) so the Vue
// components can reuse the exact same reasoning the prototype used.

const CONF_SCORE = { high: 3, medium: 2, low: 1 }

export function fmt(n) {
  return Number.isInteger(n) ? `${n}` : `${Math.round(n * 100) / 100}`
}

function sourcePapers(provenance) {
  return [...new Set((provenance || []).filter(p =>
    p && !p.includes('#') && !p.startsWith('method:') && !p.startsWith('dataset:')))]
}

export function scoreLevel(score) {
  if (score >= 6) return 'high'
  if (score >= 4) return 'moderate'
  return 'low'
}

export function scoreBreakdown(d) {
  const confidence = (d.confidence || 'low').toLowerCase()
  const confidenceScore = CONF_SCORE[confidence] ?? 1
  const papers = sourcePapers(d.provenance)
  const paperScore = papers.length * 0.5
  const realBonus = d.stub ? 0 : 2
  const calculated = confidenceScore + paperScore + realBonus
  const shown = Number.isFinite(Number(d._score)) ? Number(d._score) : calculated
  return { confidence, confidenceScore, papers, paperScore, realBonus, shown }
}

function firstText(items, field, limit = 2) {
  return (items || []).map(x => x && x[field]).filter(Boolean).slice(0, limit)
}

function describeTopic(topic, claims) {
  if (!claims.length)
    return `"${topic}" is the research idea being evaluated. The analyst is checking whether the papers contain enough evidence to support or challenge it.`
  return `"${topic}" is the research idea being evaluated. For a beginner, the easiest entry point is the paper claims: ${claims.map(c => `"${c}"`).join(' ')}`
}

export function beginnerContext(d) {
  const details = d.details || {}
  if (d.kind === 'evidence') {
    const topic = details.topic || 'this topic'
    const claims = firstText(details.supporting, 'statement')
    return describeTopic(topic, claims)
  }
  if (d.kind === 'synergy') {
    const a = details.method_a || {}
    const b = details.method_b || {}
    const left = a.description ? `"${a.name}" means ${a.description}` : `"${a.name || 'one method'}" is one technique in the corpus.`
    const right = b.description ? `"${b.name}" means ${b.description}` : `"${b.name || 'another method'}" is another technique in the corpus.`
    return `${left} ${right} The insight is about whether these two ideas could reinforce each other if combined.`
  }
  if (d.kind === 'contradiction') {
    const a = (details.claim_a || {}).statement
    const b = (details.claim_b || {}).statement
    if (a && b)
      return `This is about two paper claims that appear to pull in different directions: "${a}" versus "${b}".`
    return `This is about a possible disagreement between papers on "${details.topic || 'the same topic'}".`
  }
  if (d.kind === 'gap') {
    const method = details.method || 'the method'
    const dataset = details.missing_dataset || 'a dataset or benchmark'
    return `This is about evaluation coverage. The method "${method}" may not have been tested on "${dataset}", so we do not yet know how it behaves there.`
  }
  if (d.kind === 'hypothesis') {
    const grounded = firstText(details.grounded_in, 'statement', 1)
    const base = `This is a suggested next experiment or research direction around "${details.topic || 'this area'}".`
    return grounded.length ? `${base} It is grounded in a related claim from the corpus: "${grounded[0]}".` : base
  }
  return 'This is an analyst-generated note about a research idea found in the paper corpus.'
}

export function plainInsight(d) {
  const details = d.details || {}
  if (d.kind === 'evidence') {
    const topic = details.topic || 'this topic'
    const verdict = details.verdict || 'unclear'
    const supporting = (details.supporting || []).length
    const contradicting = (details.contradicting || []).length
    const summary = details.summary ? ` In short: ${details.summary}` : ''
    return `The analyst checked whether the papers support "${topic}" and judged the evidence as ${verdict}. It found ${supporting} supporting claim(s) and ${contradicting} contradicting claim(s).${summary}`
  }
  if (d.kind === 'synergy') {
    const a = (details.method_a || {}).name || 'one method'
    const b = (details.method_b || {}).name || 'another method'
    const rationale = details.rationale ? ` ${details.rationale}` : ''
    return `The analyst thinks "${a}" and "${b}" could be useful together.${rationale}`
  }
  if (d.kind === 'contradiction') {
    const topic = details.topic || 'the topic'
    const explanation = details.explanation ? ` ${details.explanation}` : ''
    return `The analyst found two claims that may disagree about "${topic}".${explanation}`
  }
  if (d.kind === 'gap') {
    const method = details.method || 'this method'
    const dataset = details.missing_dataset || 'a dataset'
    const peer = details.evaluated_by ? ` A peer method, "${details.evaluated_by}", was evaluated there.` : ''
    return `The analyst found a coverage gap: "${method}" does not appear to have been evaluated on "${dataset}".${peer}`
  }
  if (d.kind === 'hypothesis') {
    const topic = details.topic || 'this area'
    const rationale = details.rationale ? ` ${details.rationale}` : ''
    return `This is a proposed research direction for "${topic}".${rationale}`
  }
  if (details.summary) return details.summary
  return d.summary || 'No summary was recorded for this insight.'
}

export function scoreNarrative(d, parts) {
  const level = scoreLevel(parts.shown)
  const paperText = parts.papers.length
    ? `${parts.papers.length} distinct source paper(s) add ${fmt(parts.paperScore)} point(s)`
    : 'no distinct source-paper IDs add breadth points'
  const stubText = d.stub
    ? 'it came from the offline stub, so it gets no real-reasoning bonus'
    : 'it came from the real reasoning path, adding 2 points'
  return `This is a ${level} score because confidence is ${parts.confidence} (${fmt(parts.confidenceScore)} point(s)), ${paperText}, and ${stubText}.`
}
