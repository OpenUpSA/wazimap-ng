python3 manage.py migrate
python3 manage.py loadshp /fixtures/za-simplified/za.shp a-simplified/za.shp code=code,parent=parent_code,name=name,area=area planning_region version_0
python3 manage.py loadshp /fixtures/pr-simplified/pr.shp a-simplified/za.shp code=code,parent_cod=parent_code,name=name,area=area planning_region version_0
python3 manage.py load_data

