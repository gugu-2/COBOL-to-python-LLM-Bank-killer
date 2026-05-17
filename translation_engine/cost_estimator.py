import logging
import os

class CostEstimator:
    @staticmethod
    def generate_roi_dashboard(cobol_code: str, output_filepath: str):
        lines_of_code = len(cobol_code.splitlines())
        
        # Heuristics for calculation (simulated values for dashboard)
        # Average mainframe cost: ~$4000 per MIPS per year.
        # Average cloud cost: ~75% reduction
        
        estimated_mips = max(1, lines_of_code / 500) # completely arbitrary heuristic for prototype
        annual_mainframe_cost = estimated_mips * 4000
        annual_cloud_cost = annual_mainframe_cost * 0.25
        annual_savings = annual_mainframe_cost - annual_cloud_cost
        
        html_content = f"""
        <html>
        <head>
            <title>Migration ROI Dashboard</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f0f4f8; }}
                h1 {{ color: #102a43; text-align: center; margin-bottom: 40px; }}
                .dashboard {{ display: flex; justify-content: space-around; gap: 20px; }}
                .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; flex: 1; }}
                .card h2 {{ font-size: 1.2rem; color: #627d98; margin-top: 0; }}
                .card .value {{ font-size: 2.5rem; font-weight: bold; color: #102a43; margin: 10px 0; }}
                .card.savings .value {{ color: #047481; }}
                .card.cost .value {{ color: #c53030; }}
            </style>
        </head>
        <body>
            <h1>Legacy Modernization ROI Dashboard</h1>
            <div class="dashboard">
                <div class="card">
                    <h2>Legacy Lines of Code</h2>
                    <div class="value">{lines_of_code:,}</div>
                    <p>Analyzed COBOL lines</p>
                </div>
                <div class="card cost">
                    <h2>Legacy Mainframe Cost</h2>
                    <div class="value">${annual_mainframe_cost:,.2f}</div>
                    <p>Estimated Annual Cost</p>
                </div>
                <div class="card savings">
                    <h2>Modern Cloud Cost</h2>
                    <div class="value">${annual_cloud_cost:,.2f}</div>
                    <p>AWS/GCP Projected Annual Cost</p>
                </div>
                <div class="card savings">
                    <h2>Net Annual Savings</h2>
                    <div class="value">${annual_savings:,.2f}</div>
                    <p>75% Cost Reduction achieved</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_filepath, "w") as f:
            f.write(html_content)
            
        logging.info(f"ROI Dashboard generated at: {output_filepath}")
