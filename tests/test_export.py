import os
import pytest
from services.export import export_data_to_csv

def test_csv_export():
    """اختبار تصدير البيانات إلى ملف CSV والتحقق من إنشائه"""
    success = export_data_to_csv()
    assert success is True
    assert os.path.exists("report.csv")
    
    # تنظيف الملف بعد الاختبار
    if os.path.exists("report.csv"):
        os.remove("report.csv")
