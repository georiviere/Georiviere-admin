# Generated by Django 3.1.14 on 2023-12-18 16:08

from django.db import migrations
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):

    dependencies = [
        ('river', '0039_auto_20231218_1601'),
    ]

    operations = [
        pgtrigger.migrations.RemoveTrigger(
            model_name='topology',
            name='update_topology_geom',
        ),
        pgtrigger.migrations.AddTrigger(
            model_name='topology',
            trigger=pgtrigger.compiler.Trigger(name='update_topology_geom', sql=pgtrigger.compiler.UpsertTriggerSql(declare='DECLARE stream_geom geometry;', func='\n                        SELECT r.geom FROM river_stream r WHERE NEW.stream_id = r.id INTO stream_geom;\n                        UPDATE description_morphology\n                        SET geom = ST_LINESUBSTRING(stream_geom, NEW.start_position, NEW.end_position)\n                        WHERE topology_id = NEW.id; \n                        UPDATE description_status\n                        SET geom = ST_LINESUBSTRING(stream_geom, NEW.start_position, NEW.end_position)\n                        WHERE topology_id = NEW.id; \n                    RETURN NEW;\n                ', hash='4d63b6e0ef200235882742af37d834d00b5a271a', operation='UPDATE OR INSERT', pgid='pgtrigger_update_topology_geom_011ed', table='river_topology', when='AFTER')),
        ),
    ]
