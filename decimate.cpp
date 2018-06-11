#include <igl/qslim.h>

#if defined(_WIN32)
#define POLYSLIM_EXPORT   __declspec(dllexport)
#else
#define POLYSLIM_EXPORT
#endif

extern "C" {
  struct vec3 {
    float x, y, z;
  };

  struct face {
    int v[3];
  };

  POLYSLIM_EXPORT bool decimate(vec3* vertices, int vertex_count, face* faces, int face_count, int target_face_count, int* out_vertex_count, int* out_face_count) {
    // printf("decimate() called on %d vertices and %d faces.\n", vertex_count, face_count);
    // for (int i=0; i<vertex_count; i++) {
    //   printf("    Vert %d: %0.1f, %0.1f, %0.1f\n", i, vertices[i].x, vertices[i].y, vertices[i].z);
    // }
    // for (int i=0; i<face_count; i++) {
    //   printf("    Face %d: %d, %d, %d\n", i, faces[i].v[0], faces[i].v[1], faces[i].v[2]);
    // }

    *out_vertex_count = 0;
    *out_face_count = 0;

    Eigen::MatrixXd everts(vertex_count, 3);
    Eigen::MatrixXi efaces(face_count, 3);

    for (int i=0; i<vertex_count; i++) {
      everts(i, 0) = vertices[i].x;
      everts(i, 1) = vertices[i].y;
      everts(i, 2) = vertices[i].z;
    }
    for (int i=0; i<face_count; i++) {
      efaces(i, 0) = faces[i].v[0];
      efaces(i, 1) = faces[i].v[1];
      efaces(i, 2) = faces[i].v[2];
    }

    Eigen::MatrixXd U;
    Eigen::MatrixXi G;
    Eigen::VectorXi J;
    Eigen::VectorXi I;

    bool res = igl::qslim(everts,
                          efaces,
                          target_face_count,
                          U,
                          G,
                          J,
                          I);

    // printf("qslim() result: %s / %d vertices / %d faces.\n", (res) ? "success" : "failure", (int)U.rows(), (int)G.rows());
    // for (int i=0; i<U.rows(); i++) {
    //   printf("    Vert %d: %0.1f, %0.1f, %0.1f\n", i, U(i, 0), U(i, 1), U(i, 2));
    // }
    // for (int i=0; i<G.rows(); i++) {
    //   printf("    Face %d: %d, %d, %d\n", i, G(i, 0), G(i, 1), G(i, 2));
    // }

    if (res) {
      *out_vertex_count = U.rows();
      *out_face_count = G.rows();

      for (int i=0; i<U.rows(); i++) {
        vec3& v = vertices[i];
        v.x = U(i, 0);
        v.y = U(i, 1);
        v.z = U(i, 2);
      }
      for (int i=0; i<G.rows(); i++) {
        face & f = faces[i];
        f.v[0] = G(i, 0);
        f.v[1] = G(i, 1);
        f.v[2] = G(i, 2);
      }
    }

    return res;
  }
}
