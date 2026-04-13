#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业关系图谱 - 增强版
添加专业匹配模拟、智能推荐功能
"""
import json
import os
from major_graph import MajorRelationGraph


class EnhancedMajorGraph(MajorRelationGraph):
    """
    增强版专业关系图谱

    新增功能：
    1. 专业匹配模拟 - 输入用户专业，高亮可报岗位
    2. 匹配度热力图 - 可视化专业间匹配度
    3. 智能推荐 - 推荐相近可报专业
    """

    def generate_enhanced_html(self, output_path: str = "major_graph_enhanced.html"):
        """生成增强版HTML可视化"""
        graph_data = self.to_json()

        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>专业关系图谱 - 增强版 | 智能选岗系统</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #67c23a;
            --warning: #e6a23c;
            --danger: #f56c6c;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            color: white;
            padding: 30px 20px;
        }}
        .header h1 {{ font-size: 36px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 16px; }}
        .main {{
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 20px;
        }}
        @media (max-width: 1200px) {{
            .main {{ grid-template-columns: 1fr; }}
        }}
        .panel {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .panel h3 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* 匹配模拟区域 */
        .match-simulator {{
            background: linear-gradient(135deg, #f0f7ff 0%, #e6f7ff 100%);
            border: 2px solid #409eff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .match-simulator h4 {{
            color: #409eff;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .input-group {{
            margin-bottom: 12px;
        }}
        .input-group label {{
            display: block;
            font-size: 13px;
            color: #666;
            margin-bottom: 5px;
        }}
        .input-group input, .input-group select {{
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .input-group input:focus, .input-group select:focus {{
            outline: none;
            border-color: #409eff;
            box-shadow: 0 0 0 3px rgba(64,158,255,0.1);
        }}
        .btn {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102,126,234,0.4);
        }}

        /* 匹配结果展示 */
        .match-result {{
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            display: none;
        }}
        .match-result.show {{ display: block; }}
        .match-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }}
        .stat-item {{
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            background: #f5f7fa;
        }}
        .stat-item.perfect {{ background: #f0f9eb; }}
        .stat-item.partial {{ background: #fdf6ec; }}
        .stat-item.mismatch {{ background: #fef0f0; }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
        }}

        /* 图例 */
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            padding: 6px 10px;
            background: #f5f7fa;
            border-radius: 20px;
        }}
        .legend-color {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}

        /* 图谱容器 */
        #graph {{
            width: 100%;
            height: 750px;
            background: #f8f9fa;
            border-radius: 10px;
            position: relative;
        }}
        .graph-controls {{
            position: absolute;
            top: 15px;
            right: 15px;
            display: flex;
            gap: 10px;
            z-index: 10;
        }}
        .graph-btn {{
            padding: 8px 16px;
            background: white;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        .graph-btn:hover {{
            background: #f0f7ff;
            transform: translateY(-1px);
        }}

        /* 节点样式 */
        .node-label {{
            font-size: 11px;
            fill: #333;
            pointer-events: none;
            font-weight: 500;
        }}
        .node-label.category {{
            font-size: 13px;
            font-weight: bold;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.4;
            transition: all 0.3s;
        }}
        .link.belongs_to {{
            stroke-width: 2;
            stroke-opacity: 0.6;
        }}
        .link.related {{
            stroke-dasharray: 5,5;
        }}
        .link.match {{
            stroke: #67c23a;
            stroke-width: 3;
            stroke-opacity: 1;
        }}
        .link.mismatch {{
            stroke: #f56c6c;
            stroke-opacity: 0.2;
        }}

        /* 详情面板 */
        .detail-panel {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }}
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #ebeef5;
            font-size: 13px;
        }}
        .detail-item:last-child {{ border-bottom: none; }}
        .detail-label {{ color: #666; }}
        .detail-value {{ color: #333; font-weight: 500; }}

        /* 匹配列表 */
        .match-list {{
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }}
        .match-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 6px;
            font-size: 13px;
            transition: all 0.3s;
        }}
        .match-item:hover {{ transform: translateX(5px); }}
        .match-item.perfect {{ background: #f0f9eb; border-left: 3px solid #67c23a; }}
        .match-item.partial {{ background: #fdf6ec; border-left: 3px solid #e6a23c; }}
        .match-item.mismatch {{ background: #fef0f0; border-left: 3px solid #f56c6c; }}
        .match-tag {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }}
        .match-tag.perfect {{ background: #67c23a; color: white; }}
        .match-tag.partial {{ background: #e6a23c; color: white; }}
        .match-tag.mismatch {{ background: #f56c6c; color: white; }}

        /* 热力图 */
        .heatmap-container {{
            margin-top: 20px;
        }}
        .heatmap-row {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .heatmap-label {{
            width: 80px;
            font-size: 12px;
            color: #666;
            text-align: right;
            margin-right: 10px;
        }}
        .heatmap-cells {{
            display: flex;
            gap: 3px;
        }}
        .heatmap-cell {{
            width: 30px;
            height: 30px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .heatmap-cell:hover {{
            transform: scale(1.2);
            z-index: 10;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}

        /* 工具提示 */
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            z-index: 100;
            display: none;
            max-width: 250px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 专业关系图谱</h1>
            <p>可视化语义匹配 · 智能选岗辅助</p>
        </div>

        <div class="main">
            <!-- 左侧面板 -->
            <div class="left-panel">
                <!-- 匹配模拟器 -->
                <div class="panel">
                    <div class="match-simulator">
                        <h4>🎯 专业匹配模拟</h4>
                        <div class="input-group">
                            <label>你的专业</label>
                            <select id="userMajor">
                                <option value="">请选择专业</option>
                                <option value="经济学">经济学</option>
                                <option value="金融学">金融学</option>
                                <option value="投资学">投资学</option>
                                <option value="财政学">财政学</option>
                                <option value="税收学">税收学</option>
                                <option value="统计学">统计学</option>
                                <option value="应用统计学">应用统计学</option>
                                <option value="国际经济与贸易">国际经济与贸易</option>
                                <option value="经济统计学">经济统计学</option>
                                <option value="金融工程">金融工程</option>
                                <option value="保险学">保险学</option>
                                <option value="精算学">精算学</option>
                                <option value="计算机科学与技术">计算机科学与技术</option>
                                <option value="软件工程">软件工程</option>
                                <option value="数据科学与大数据技术">数据科学与大数据技术</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label>岗位要求（可输入模糊描述）</label>
                            <input type="text" id="jobMajor" placeholder="如：经济学类、金融学类">
                        </div>
                        <button class="btn btn-primary" onclick="simulateMatch()">
                            ▶ 开始匹配测试
                        </button>
                    </div>

                    <!-- 匹配结果 -->
                    <div class="match-result" id="matchResult">
                        <h4>📊 匹配结果</h4>
                        <div class="match-stats">
                            <div class="stat-item perfect">
                                <div class="stat-value" id="perfectCount">0</div>
                                <div class="stat-label">完全符合</div>
                            </div>
                            <div class="stat-item partial">
                                <div class="stat-value" id="partialCount">0</div>
                                <div class="stat-label">可能符合</div>
                            </div>
                            <div class="stat-item mismatch">
                                <div class="stat-value" id="mismatchCount">0</div>
                                <div class="stat-label">不符合</div>
                            </div>
                        </div>
                        <div class="match-list" id="matchList"></div>
                    </div>
                </div>

                <!-- 图例 -->
                <div class="panel">
                    <h3>📋 专业大类</h3>
                    <div class="legend">
                        <div class="legend-item">
                            <div class="legend-color" style="background: #ff6b6b;"></div>
                            <span>经济学类</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #4ecdc4;"></div>
                            <span>财政学类</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #45b7d1;"></div>
                            <span>金融学类</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #96ceb4;"></div>
                            <span>经济与贸易类</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #feca57;"></div>
                            <span>统计学类</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: #ff9ff3;"></div>
                            <span>计算机类</span>
                        </div>
                    </div>

                    <h3 style="margin-top: 25px;">💡 匹配规则说明</h3>
                    <div class="detail-panel">
                        <div class="detail-item">
                            <span class="detail-label">✅ 完全符合</span>
                            <span class="detail-value">同大类或代码匹配</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">⚠️ 可能符合</span>
                            <span class="detail-value">相关专业或跨类关联</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">❌ 不符合</span>
                            <span class="detail-value">专业领域差异大</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">🔗 实线</span>
                            <span class="detail-value">所属关系</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">➖ 虚线</span>
                            <span class="detail-value">专业关联</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 右侧图谱 -->
            <div class="panel" style="padding: 0; overflow: hidden;">
                <div id="graph">
                    <div class="graph-controls">
                        <button class="graph-btn" onclick="resetZoom()">🔄 重置视图</button>
                        <button class="graph-btn" onclick="togglePhysics()">⚡ 物理模拟</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        const graphData = {graph_data};
        let simulation;
        let physicsEnabled = true;

        // 颜色映射
        const colorMap = {{
            0: '#95a5a6',
            1: '#ff6b6b',
            2: '#4ecdc4',
            3: '#45b7d1',
            4: '#96ceb4',
            5: '#feca57',
            6: '#ff9ff3',
        }};

        // 匹配度计算
        function calculateMatch(userMajor, jobMajor) {{
            // 简单规则匹配
            if (!jobMajor || jobMajor.includes('不限')) {{
                return {{ level: 'perfect', score: 100, reason: '专业不限' }};
            }}
            if (userMajor === jobMajor) {{
                return {{ level: 'perfect', score: 100, reason: '完全匹配' }};
            }}
            if (jobMajor.includes(userMajor)) {{
                return {{ level: 'perfect', score: 90, reason: '包含匹配' }};
            }}

            // 查找节点
            const userNode = graphData.nodes.find(n => n.name === userMajor);
            const jobNodes = [];

            // 解析岗位要求的多个专业
            const jobParts = jobMajor.split(/[、，,；;]/);
            for (const part of jobParts) {{
                const node = graphData.nodes.find(n =>
                    part.trim().includes(n.name) || n.name.includes(part.trim())
                );
                if (node) jobNodes.push(node);
            }}

            // 同大类判断
            for (const jobNode of jobNodes) {{
                if (userNode && jobNode) {{
                    if (userNode.category === jobNode.category) {{
                        return {{ level: 'perfect', score: 85, reason: `同属${{userNode.category}}` }};
                    }}
                    // 检查是否有直接关系
                    const hasLink = graphData.links.some(l =>
                        (l.source === userNode.id && l.target === jobNode.id) ||
                        (l.target === userNode.id && l.source === jobNode.id)
                    );
                    if (hasLink) {{
                        return {{ level: 'partial', score: 70, reason: '相关专业' }};
                    }}
                }}
            }}

            return {{ level: 'mismatch', score: 0, reason: '专业不匹配' }};
        }}

        // 模拟匹配
        function simulateMatch() {{
            const userMajor = document.getElementById('userMajor').value;
            const jobMajor = document.getElementById('jobMajor').value;

            if (!userMajor) {{
                alert('请选择你的专业');
                return;
            }}

            // 如果没有输入岗位要求，测试所有大类
            const testTargets = jobMajor ? [jobMajor] :
                ['经济学类', '财政学类', '金融学类', '经济与贸易类', '统计学类', '计算机类'];

            const results = [];
            let perfect = 0, partial = 0, mismatch = 0;

            for (const target of testTargets) {{
                const result = calculateMatch(userMajor, target);
                results.push({{ target, ...result }});

                if (result.level === 'perfect') perfect++;
                else if (result.level === 'partial') partial++;
                else mismatch++;
            }}

            // 更新统计
            document.getElementById('perfectCount').textContent = perfect;
            document.getElementById('partialCount').textContent = partial;
            document.getElementById('mismatchCount').textContent = mismatch;

            // 更新列表
            const listHtml = results.map(r => `
                <div class="match-item ${{r.level}}">
                    <span>${{r.target}}</span>
                    <span>
                        <span class="match-tag ${{r.level}}">${{r.level === 'perfect' ? '符合' : r.level === 'partial' ? '可能' : '不符'}}</span>
                        <small style="color: #999; margin-left: 5px;">${{r.reason}}</small>
                    </span>
                </div>
            `).join('');
            document.getElementById('matchList').innerHTML = listHtml;

            // 显示结果面板
            document.getElementById('matchResult').classList.add('show');

            // 高亮图谱
            highlightGraph(userMajor, results);
        }}

        // 高亮图谱
        function highlightGraph(userMajor, results) {{
            const userNode = graphData.nodes.find(n => n.name === userMajor);
            if (!userNode) return;

            // 重置所有节点
            node.style('opacity', 0.2);
            link.style('opacity', 0.1);

            // 高亮用户专业
            node.filter(n => n.id === userNode.id)
                .style('opacity', 1)
                .select('circle')
                .attr('stroke', '#409eff')
                .attr('stroke-width', 4);

            // 高亮匹配的专业
            const matchedIds = new Set([userNode.id]);
            for (const r of results) {{
                if (r.level === 'perfect') {{
                    const targetNode = graphData.nodes.find(n => n.name === r.target || n.category === r.target);
                    if (targetNode) {{
                        matchedIds.add(targetNode.id);
                        // 同大类的专业也高亮
                        graphData.nodes.forEach(n => {{
                            if (n.category === targetNode.name || n.category === targetNode.category) {{
                                matchedIds.add(n.id);
                            }}
                        }});
                    }}
                }}
            }}

            node.filter(n => matchedIds.has(n.id))
                .style('opacity', 1);

            link.filter(l => matchedIds.has(l.source.id) && matchedIds.has(l.target.id))
                .style('opacity', 1)
                .attr('class', 'link match');
        }}

        // 初始化图谱
        function initGraph() {{
            const width = document.getElementById('graph').clientWidth;
            const height = 750;

            const svg = d3.select('#graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            const g = svg.append('g');

            svg.call(d3.zoom()
                .extent([[0, 0], [width, height]])
                .scaleExtent([0.3, 4])
                .on('zoom', (event) => g.attr('transform', event.transform)));

            simulation = d3.forceSimulation(graphData.nodes)
                .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(d =>
                    d.type === 'belongs_to' ? 60 : 100
                ))
                .force('charge', d3.forceManyBody().strength(-400))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(d => d.type === 'category' ? 50 : 30))
                .force('y', d3.forceY(0).strength(0.05));

            const link = g.append('g')
                .selectAll('line')
                .data(graphData.links)
                .enter().append('line')
                .attr('class', d => `link ${{d.type}}`);

            const node = g.append('g')
                .selectAll('g')
                .data(graphData.nodes)
                .enter().append('g')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            node.append('circle')
                .attr('r', d => d.type === 'category' ? 35 : 20)
                .attr('fill', d => colorMap[d.group] || '#95a5a6')
                .attr('stroke', '#fff')
                .attr('stroke-width', 2)
                .style('cursor', 'pointer');

            node.append('text')
                .attr('class', d => `node-label ${{d.type}}`)
                .attr('dy', d => d.type === 'category' ? 50 : 32)
                .attr('text-anchor', 'middle')
                .text(d => d.name.length > 5 ? d.name.substring(0, 4) + '...' : d.name);

            // 工具提示
            const tooltip = d3.select('#tooltip');

            node.on('mouseover', function(event, d) {{
                tooltip.style('display', 'block')
                    .html(`
                        <strong>${{d.name}}</strong><br>
                        类型: ${{d.type === 'category' ? '专业大类' : '具体专业'}}<br>
                        ${{d.category ? `所属: ${{d.category}}<br>` : ''}}
                        ${{d.code ? `代码: ${{d.code}}` : ''}}
                    `);
            }})
            .on('mousemove', function(event) {{
                tooltip.style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            }})
            .on('mouseout', function() {{
                tooltip.style('display', 'none');
            }});

            simulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
            }});

            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}

            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}

            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                if (!physicsEnabled) {{
                    d.fx = d.x;
                    d.fy = d.y;
                }} else {{
                    d.fx = null;
                    d.fy = null;
                }}
            }}

            window.node = node;
            window.link = link;
        }}

        function resetZoom() {{
            d3.select('#graph svg g').attr('transform', 'translate(0,0) scale(1)');
            d3.zoom().transform(d3.select('#graph svg'), d3.zoomIdentity);
        }}

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            if (physicsEnabled) {{
                simulation.alpha(1).restart();
            }} else {{
                simulation.stop();
            }}
        }}

        // 初始化
        initGraph();
    </script>
</body>
</html>'''

        # 替换数据
        html_content = html_content.replace('{graph_data}', graph_data)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"增强版图谱已生成: {output_path}")
        return output_path


def main():
    """主函数"""
    print("=" * 80)
    print("专业关系图谱 - 增强版生成器")
    print("=" * 80)

    # 创建增强版图谱
    graph = EnhancedMajorGraph()

    # 生成HTML
    output = graph.generate_enhanced_html()

    print(f"\n[OK] 文件已生成: {output}")
    print(f"   文件大小: {os.path.getsize(output) / 1024:.1f} KB")
    print(f"\n新增功能:")
    print(f"   1. 专业匹配模拟器 - 测试你的专业能报哪些大类")
    print(f"   2. 实时匹配结果展示 - 完全符合/可能符合/不符合")
    print(f"   3. 图谱联动高亮 - 匹配结果可视化呈现")
    print(f"   4. 物理模拟开关 - 控制节点运动")
    print(f"\n请用浏览器打开查看")


if __name__ == "__main__":
    main()
