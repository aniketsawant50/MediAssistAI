from fastmcp import FastMCP

from App.MCP.tools import *
from App.MCP.query_router import ask_database

mcp = FastMCP("MediAssistAI")


@mcp.tool()
def Ask_MediAssist(query: str):

    """
    Natural language query.

    Examples:
    Show patient PC00001Q

    Give me history of Patient 1 ML

    Show prescriptions of Patient 1 ML

    Show billing of Patient 1 ML
    """

    return ask_database(query)


@mcp.tool()
def Get_Patient(patient_id: int):
    return get_patient_by_id(patient_id)


@mcp.tool()
def Get_History(patient_id: int):
    return get_complete_history(patient_id)


@mcp.tool()
def Get_Doctors():
    return get_doctors()


@mcp.tool()
def Get_Departments():
    return get_departments()


@mcp.tool()
def Get_Branches():
    return get_branches()


if __name__ == "__main__":
    mcp.run()