#include <stdint.h>

#define BITSET_WORD unsigned int

typedef enum {
    false,
    true
} bool;

typedef enum ENUM_PACKED {
     nir_instr_type_alu,
     nir_instr_type_deref,
     nir_instr_type_call,
     nir_instr_type_tex,
     nir_instr_type_intrinsic,
     nir_instr_type_load_const,
     nir_instr_type_jump,
     nir_instr_type_undef,
     nir_instr_type_phi,
     nir_instr_type_parallel_copy,
  } nir_instr_type;

struct exec_node {
     struct exec_node *next;
     struct exec_node *prev;
};

typedef enum {
     nir_cf_node_block,
     nir_cf_node_if,
     nir_cf_node_loop,
     nir_cf_node_function
  } nir_cf_node_type;

typedef struct nir_cf_node {
     struct exec_node node;
     nir_cf_node_type type;
     struct nir_cf_node *parent;
} nir_cf_node;

struct exec_list {
     struct exec_node head_sentinel;
     struct exec_node tail_sentinel;
};

typedef struct nir_block {
   nir_cf_node cf_node;
   struct exec_list instr_list;
   unsigned index;
   bool divergent;
   struct nir_block *successors[2];
   struct set *predecessors;
   struct nir_block *imm_dom;
   unsigned num_dom_children;
   struct nir_block **dom_children;
   struct set *dom_frontier;
   uint32_t dom_pre_index, dom_post_index;
   uint32_t start_ip;
   uint32_t end_ip;
   BITSET_WORD *live_in;
   BITSET_WORD *live_out;
} nir_block;

typedef struct nir_instr {
     struct exec_node node;
     nir_block *block;
     nir_instr_type type;
  
     uint8_t pass_flags;
     
     bool has_debug_info;
  
     uint32_t index;
} nir_instr;

