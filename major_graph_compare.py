#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业对比可视化工具
包含完整的28个专业大类 + 专业对比功能
"""
from major_graph_complete import CompleteMajorGraph


class MajorCompareVisualizer(CompleteMajorGraph):
    """专业对比可视化器"""

    def generate_compare_html(self, output_path: str = "major_compare.html"):
        """生成专业对比可视化HTML"""
        graph_data = self.to_json()

        # 获取所有专业名称用于下拉选择
        all_majors = sorted([n.name for n in self.nodes.values() if n.type == "major"])

        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>专业对比工具 | 智能选岗系统</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
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
            grid-template-columns: 400px 1fr;
            gap: 20px;
        }}
        @media (max-width: 1100px) {{
            .main {{ grid-template-columns: 1fr; }}
        }}
        .panel {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}

        /* 对比选择器 */
        .compare-selector {{
            background: linear-gradient(135deg, #f0f7ff 0%, #e6f7ff 100%);
            border: 2px solid #409eff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .compare-selector h4 {{
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
        .input-group select {{
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }}
        .btn {{
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .btn:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}

        /* 对比结果 */
        .compare-result {{
            display: none;
            margin-top: 20px;
        }}
        .compare-result.show {{ display: block; }}

        .score-card {{
            text-align: center;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .score-card.high {{
            background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
            color: white;
        }}
        .score-card.medium {{
            background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
            color: white;
        }}
        .score-card.low {{
            background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
            color: white;
        }}
        .score-value {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .score-label {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .detail-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .detail-item {{
            background: #f5f7fa;
            padding: 15px;
            border-radius: 8px;
        }}
        .detail-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        .detail-value {{
            font-size: 14px;
            font-weight: 500;
            color: #333;
        }}

        .path-container {{
            background: #f0f7ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .path-title {{
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
        }}
        .path-steps {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .path-step {{
            background: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 13px;
            border: 2px solid #409eff;
        }}
        .path-arrow {{
            color: #409eff;
            font-weight: bold;
        }}

        .suggestion {{
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.6;
        }}
        .suggestion.ok {{
            background: #f0f9eb;
            border-left: 4px solid #67c23a;
            color: #67c23a;
        }}
        .suggestion.maybe {{
            background: #fdf6ec;
            border-left: 4px solid #e6a23c;
            color: #e6a23c;
        }}
        .suggestion.no {{
            background: #fef0f0;
            border-left: 4px solid #f56c6c;
            color: #f56c6c;
        }}

        /* 图表面板 */
        #graph {{
            width: 100%;
            height: 600px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>专业对比工具</h1>
            <p>可视化分析两个专业之间的关联关系</p>
        </div>

        <div class="main">
            <div class="left-panel">
                <!-- 对比选择器 -->
                <div class="panel">
                    <div class="compare-selector">
                        <h4>选择要对比的专业</h4>
                        <div class="input-group">
                            <label>你的专业</label>
                            <select id="major1">
                                <option value="">请选择</option>
                                {''.join([f'<option value="{m}">{m}</option>' for m in all_majors])}
                            </select>
                        </div>
                        <div class="input-group">
                            <label>岗位要求的专业</label>
                            <select id="major2">
                                <option value="">请选择</option>
                                {''.join([f'<option value="{m}">{m}</option>' for m in all_majors])}
                            </select>
                        </div>
                        <button class="btn" onclick="compareMajors()">开始对比分析</button>
                    </div>

                    <!-- 对比结果 -->
                    <div class="compare-result" id="compareResult">
                        <div class="score-card" id="scoreCard">
                            <div class="score-value" id="scoreValue">0</div>
                            <div class="score-label" id="scoreLabel">关联度评分</div>
                        </div>

                        <div class="detail-grid">
                            <div class="detail-item">
                                <div class="detail-label">你的专业大类</div>
                                <div class="detail-value" id="cat1">-</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">岗位要求大类</div>
                                <div class="detail-value" id="cat2">-</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">专业代码</div>
                                <div class="detail-value" id="code1">-</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">专业代码</div>
                                <div class="detail-value" id="code2">-</div>
                            </div>
                        </div>

                        <div class="path-container">
                            <div class="path-title">关联路径</div>
                            <div class="path-steps" id="pathSteps"></div>
                        </div>

                        <div class="suggestion" id="suggestion"></div>
                    </div>
                </div>
            </div>

            <div class="panel" style="padding: 0; overflow: hidden;">
                <div id="graph"></div>
            </div>
        </div>
    </div>

    <script>
        const graphData = {graph_data};

        // 颜色映射
        const colorMap = {{
            0: '#95a5a6',
            1: '#ff6b6b', 2: '#4ecdc4', 3: '#45b7d1',
            4: '#96ceb4', 5: '#feca57', 6: '#ff9ff3',
            7: '#54a0ff', 8: '#5f27cd', 9: '#00d2d3',
            10: '#ff9f43', 11: '#ee5a24', 12: '#009432',
            13: '#0652dd', 14: '#9980fa', 15: '#c56cf0',
        }};

        // 对比专业
        function compareMajors() {{
            const m1 = document.getElementById('major1').value;
            const m2 = document.getElementById('major2').value;

            if (!m1 || !m2) {{
                alert('请选择两个专业');
                return;
            }}

            const node1 = graphData.nodes.find(n => n.name === m1);
            const node2 = graphData.nodes.find(n => n.name === m2);

            if (!node1 || !node2) {{
                alert('专业未找到');
                return;
            }}

            // 计算关联度
            let score = 0;
            let level = '';
            let suggestion = '';
            let suggestionClass = '';

            if (node1.category === node2.category) {{
                score = 100;
                level = '完全相关';
                suggestion = '[OK] ' + m1 + '和' + m2 + '同属' + node1.category + '，可以相互报考';
                suggestionClass = 'ok';
            }} else if (isRelated(node1, node2)) {{
                score = 80;
                level = '高度相关';
                suggestion = '[OK] ' + m1 + '和' + m2 + '是相关专业，大概率可以报考';
                suggestionClass = 'ok';
            }} else if (hasIndirectRelation(node1, node2)) {{
                score = 50;
                level = '中度相关';
                suggestion = '[MAYBE] ' + m1 + '和' + m2 + '有一定关联，建议咨询招考单位';
                suggestionClass = 'maybe';
            }} else {{
                score = 0;
                level = '低度相关';
                suggestion = '[NO] ' + m1 + '和' + m2 + '专业差异较大，不建议跨专业报考';
                suggestionClass = 'no';
            }}

            // 更新显示
            document.getElementById('compareResult').classList.add('show');

            const scoreCard = document.getElementById('scoreCard');
            scoreCard.className = 'score-card ' + (score >= 80 ? 'high' : score >= 50 ? 'medium' : 'low');
            document.getElementById('scoreValue').textContent = score;
            document.getElementById('scoreLabel').textContent = level;

            document.getElementById('cat1').textContent = node1.category || '-';
            document.getElementById('cat2').textContent = node2.category || '-';
            document.getElementById('code1').textContent = node1.code || '-';
            document.getElementById('code2').textContent = node2.code || '-';

            // 路径显示
            const pathSteps = document.getElementById('pathSteps');
            if (score >= 80) {{
                pathSteps.innerHTML = '<span class="path-step">' + m1 + '</span>' +
                    '<span class="path-arrow">→</span>' +
                    '<span class="path-step">' + level + '</span>' +
                    '<span class="path-arrow">→</span>' +
                    '<span class="path-step">' + m2 + '</span>';
            }} else {{
                pathSteps.innerHTML = '<span class="path-step">' + m1 + '</span>' +
                    '<span class="path-arrow">→</span>' +
                    '<span class="path-step">' + node1.category + '</span>' +
                    '<span class="path-arrow">→</span>' +
                    '<span class="path-step">不同大类</span>' +
                    '<span class="path-arrow">→</span>' +
                    '<span class="path-step">' + node2.category + '</span>' +
                    '<span class="path-arrow">→</span>' +
                    '<span class="path-step">' + m2 + '</span>';
            }}

            const sugDiv = document.getElementById('suggestion');
            sugDiv.className = 'suggestion ' + suggestionClass;
            sugDiv.textContent = suggestion;

            // 高亮图谱
            highlightGraph(node1.id, node2.id, score);
        }}

        function isRelated(n1, n2) {{
            return graphData.links.some(l =>
                (l.source === n1.id && l.target === n2.id) ||
                (l.target === n1.id && l.source === n2.id)
            );
        }}

        function hasIndirectRelation(n1, n2) {{
            // 通过大类间接关联
            return n1.category && n2.category;
        }}

        // 初始化图谱
        function initGraph() {{
            const width = document.getElementById('graph').clientWidth;
            const height = 600;

            const svg = d3.select('#graph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            const g = svg.append('g');

            svg.call(d3.zoom()
                .extent([[0, 0], [width, height]])
                .scaleExtent([0.2, 4])
                .on('zoom', (event) => g.attr('transform', event.transform)));

            const simulation = d3.forceSimulation(graphData.nodes)
                .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(80))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(d => d.type === 'category' ? 40 : 25));

            const link = g.append('g')
                .selectAll('line')
                .data(graphData.links)
                .enter().append('line')
                .attr('stroke', '#999')
                .attr('stroke-opacity', 0.4)
                .attr('stroke-width', d => d.type === 'belongs_to' ? 2 : 1);

            const node = g.append('g')
                .selectAll('g')
                .data(graphData.nodes)
                .enter().append('g')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            window.allNodes = node;
            window.allLinks = link;

            node.append('circle')
                .attr('r', d => d.type === 'category' ? 30 : 18)
                .attr('fill', d => colorMap[d.group] || '#95a5a6')
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);

            node.append('text')
                .attr('dy', d => d.type === 'category' ? 45 : 28)
                .attr('text-anchor', 'middle')
                .style('font-size', d => d.type === 'category' ? '12px' : '10px')
                .style('fill', '#333')
                .text(d => d.name.length > 4 ? d.name.substring(0, 3) + '...' : d.name);

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
                d.fx = null;
                d.fy = null;
            }}
        }}

        // 高亮显示
        function highlightGraph(id1, id2, score) {{
            window.allNodes.style('opacity', 0.2);
            window.allLinks.style('opacity', 0.1);

            // 高亮选中的两个节点
            window.allNodes.filter(d => d.id === id1 || d.id === id2)
                .style('opacity', 1)
                .select('circle')
                .attr('stroke', score >= 80 ? '#67c23a' : score >= 50 ? '#e6a23c' : '#f56c6c')
                .attr('stroke-width', 4);

            // 高亮连接线
            window.allLinks.filter(l =>
                (l.source.id === id1 && l.target.id === id2) ||
                (l.source.id === id2 && l.target.id === id1)
            ).style('opacity', 1)
             .attr('stroke', score >= 80 ? '#67c23a' : score >= 50 ? '#e6a23c' : '#f56c6c')
             .attr('stroke-width', 3);
        }}

        initGraph();
    </script>
</body>
</html>'''

        # 替换数据
        html_content = html_content.replace('{graph_data}', graph_data)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path


if __name__ == "__main__":
    print("=" * 80)
    print("专业对比可视化工具")
    print("=" * 80)

    # 创建可视化器
    visualizer = MajorCompareVisualizer()

    # 生成HTML
    output = visualizer.generate_compare_html()

    print(f"\n[OK] 文件已生成: {output}")
    print(f"   文件大小: {len(open(output, 'r', encoding='utf-8').read()) / 1024:.1f} KB")
    print(f"\n功能说明:")
    print(f"   1. 选择两个专业进行对比")
    print(f"   2. 显示关联度评分(0-100分)")
    print(f"   3. 可视化展示关联路径")
    print(f"   4. 提供报考建议")
    print(f"\n包含28个专业大类，共206个专业")
    print(f"用浏览器打开即可使用")
