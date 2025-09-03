bl_info = {
    "name": "Import XAC (.xac)",
    "author": "OpenAI (nach Nutzerspezifikation)",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > XAC (.xac)",
    "description": "Importiert XAC-Dateien basierend auf strikten Spezifikationen",
    "category": "Import-Export",
}

import bpy
import struct
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

class XACImporter(Operator, ImportHelper):
    bl_idname = "import_scene.xac"
    bl_label = "Import XAC"
    bl_options = {"UNDO"}

    filename_ext = ".xac"
    filter_glob: StringProperty(
        default="*.xac",
        options={'HIDDEN'}
    )

    def execute(self, context):
        return self.read_xac(self.filepath, context)

    def read_string(self, f, endian):
        length = struct.unpack(endian + "I", f.read(4))[0]
        return f.read(length).decode('utf-8')

    def read_vec3d(self, f, endian):
        return struct.unpack(endian + "fff", f.read(12))

    def read_vec4d(self, f, endian):
        return struct.unpack(endian + "ffff", f.read(16))

    def read_quat(self, f, endian):
        return struct.unpack(endian + "ffff", f.read(16))

    def read_matrix44(self, f, endian):
        return [self.read_vec4d(f, endian) for _ in range(4)]

    def read_xac(self, filepath, context):
        with open(filepath, 'rb') as f:
            magic = f.read(4)
            if magic != b'XAC ':
                self.report({'ERROR'}, "Ungültige Datei: Kein XAC-Header")
                return {'CANCELLED'}

            major = struct.unpack('B', f.read(1))[0]
            minor = struct.unpack('B', f.read(1))[0]
            big_endian = struct.unpack('B', f.read(1))[0] != 0
            multiply_order = struct.unpack('B', f.read(1))[0]

            endian = ">" if big_endian else "<"
            nodes = []
            meshes = {}
            materials = []
            influence_data = {}
            influence_ranges = {}

            while True:
                header = f.read(12)
                if not header or len(header) < 12:
                    break

                chunk_type, chunk_len, chunk_ver = struct.unpack(endian + "iii", header)
                pos = f.tell()

                if chunk_type == 0xB:
                    num_nodes, num_roots = struct.unpack(endian + "ii", f.read(8))
                    for _ in range(num_nodes):
                        rot = self.read_quat(f, endian)
                        scale_rot = self.read_quat(f, endian)
                        pos3 = self.read_vec3d(f, endian)
                        scale = self.read_vec3d(f, endian)
                        f.read(12)
                        f.read(8)
                        parent_id = struct.unpack(endian + "i", f.read(4))[0]
                        num_children = struct.unpack(endian + "i", f.read(4))[0]
                        include_bounds = struct.unpack(endian + "i", f.read(4))[0]
                        transform = self.read_matrix44(f, endian)
                        importance = struct.unpack(endian + "f", f.read(4))[0]
                        name = self.read_string(f, endian)
                        nodes.append({
                            "name": name,
                            "parent": parent_id,
                            "pos": pos3,
                            "rot": rot,
                            "scale": scale,
                        })

                elif chunk_type == 0x1:
                    start_pos = f.tell()
                    chunk_data = f.read(chunk_len)
                    if len(chunk_data) < 28:
                        self.report({'WARNING'}, f"Warnung: Chunk 1 ist ungewöhnlich kurz ({len(chunk_data)} Bytes). Erzeuge Dummy-Mesh.")
                        dummy_mesh = bpy.data.meshes.new("Dummy")
                        dummy_obj = bpy.data.objects.new("Dummy", dummy_mesh)
                        context.collection.objects.link(dummy_obj)
                        dummy_mesh.from_pydata([(0,0,0), (1,0,0), (0,1,0)], [], [(0,1,2)])
                        dummy_mesh.update()
                        continue
                    ptr = 0
                    node_id, num_ir, num_verts, num_indices, num_submeshes, num_layers, b_coll = struct.unpack(endian + "7i", chunk_data[ptr:ptr+28])
                    ptr += 28

                    attribs = []
                    for _ in range(num_layers):
                        if ptr + 12 > len(chunk_data):
                            self.report({'ERROR'}, "Fehler beim Lesen eines Attribut-Layers: unvollständige Daten.")
                            return {'CANCELLED'}
                        a_type, a_size, keep, scale, _ = struct.unpack(endian + "iibbh", chunk_data[ptr:ptr+12])
                        ptr += 12
                        data_len = num_verts * a_size
                        if ptr + data_len > len(chunk_data):
                            self.report({'ERROR'}, "Fehler: Attributdaten überschreiten Chunk-Größe.")
                            return {'CANCELLED'}
                        data = chunk_data[ptr:ptr+data_len]
                        ptr += data_len
                        attribs.append({"type": a_type, "attribSize": a_size, "data": data})

                    submeshes = []
                    vertex_offset = 0
                    for _ in range(num_submeshes):
                        if ptr + 16 > len(chunk_data):
                            self.report({'ERROR'}, "Fehler beim Lesen eines Submeshes.")
                            return {'CANCELLED'}
                        ni, nv, mid, nb = struct.unpack(endian + "4i", chunk_data[ptr:ptr+16])
                        ptr += 16
                        if ptr + 4 * ni > len(chunk_data):
                            self.report({'ERROR'}, "Fehler: Zu wenig Indizes im Submesh.")
                            return {'CANCELLED'}
                        rel_indices = list(struct.unpack(endian + f"{ni}i", chunk_data[ptr:ptr + 4 * ni]))
                        ptr += 4 * ni
                        ptr += 4 * nb
                        indices = [ri + vertex_offset for ri in rel_indices]
                        vertex_offset += nv
                        submeshes.append({"indices": indices, "materialId": mid})

                    # Positionen und UVs extrahieren
                    verts = [(0, 0, 0)] * num_verts
                    uvs = [(0, 0)] * num_verts
                    for attrib in attribs:
                        if attrib["type"] == 0:  # Position
                            for i in range(num_verts):
                                offset = i * attrib["attribSize"]
                                verts[i] = struct.unpack_from(endian + "fff", attrib["data"], offset)
                        elif attrib["type"] == 3:  # UV
                            for i in range(num_verts):
                                offset = i * attrib["attribSize"]
                                uvs[i] = struct.unpack_from(endian + "ff", attrib["data"], offset)

                    mesh = bpy.data.meshes.new(f"Mesh_{node_id}")
                    obj = bpy.data.objects.new(f"Object_{node_id}", mesh)
                    context.collection.objects.link(obj)

                    all_faces = []
                    for sm in submeshes:
                        idx = sm["indices"]
                        all_faces += [tuple(idx[i:i+3]) for i in range(0, len(idx), 3)]

                    mesh.from_pydata(verts, [], all_faces)
                    mesh.update()

                    # UV Map
                    if uvs:
                        mesh.uv_layers.new(name="UVMap")
                        uv_layer = mesh.uv_layers.active.data
                        for poly in mesh.polygons:
                            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                                vi = mesh.loops[loop_index].vertex_index
                                if vi < len(uvs):
                                    uv_layer[loop_index].uv = uvs[vi]

                    meshes[node_id] = {"object": obj}

                elif chunk_type == 0x2:
                    nid, num_bones, num_infl, is_coll, *_ = struct.unpack(endian + "3iBxxx", f.read(16))
                    inf_data = []
                    for _ in range(num_infl):
                        weight = struct.unpack(endian + "f", f.read(4))[0]
                        bone_id = struct.unpack(endian + "h", f.read(2))[0]
                        f.read(2)
                        inf_data.append((weight, bone_id))
                    influence_data[nid] = inf_data
                    ranges = []
                    for _ in range(num_bones):
                        first, count = struct.unpack(endian + "ii", f.read(8))
                        ranges.append((first, count))
                    influence_ranges[nid] = ranges

                elif chunk_type == 0xD:
                    f.read(12)

                elif chunk_type == 0x3:
                    amb = self.read_vec4d(f, endian)
                    dif = self.read_vec4d(f, endian)
                    spe = self.read_vec4d(f, endian)
                    emi = self.read_vec4d(f, endian)
                    shine, stren, opac, ior = struct.unpack(endian + "ffff", f.read(16))
                    dside, wire, _, nlay = struct.unpack(endian + "4B", f.read(4))
                    name = self.read_string(f, endian)
                    layers = []
                    for _ in range(nlay):
                        amt, uofs, vofs, util, vtil, rot = struct.unpack(endian + "6f", f.read(24))
                        mid = struct.unpack(endian + "h", f.read(2))[0]
                        mtype, _ = struct.unpack(endian + "2B", f.read(2))
                        tex = self.read_string(f, endian)
                        layers.append({"texture": tex})
                    materials.append({"name": name, "layers": layers})

                elif chunk_type == 0xC:
                    f.read(chunk_len)

                else:
                    f.seek(pos + chunk_len)

        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(XACImporter.bl_idname, text="XAC (.xac)")

def register():
    bpy.utils.register_class(XACImporter)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(XACImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
