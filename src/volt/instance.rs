use std::collections::HashMap;
use std::collections::HashSet;
use std::ffi::c_char;
use std::ffi::c_void;
use std::ffi::CStr;
use std::ffi::CString;
use std::sync::Arc;
use std::mem;
use std::ptr;
use std::sync::RwLock;

use ash::vk;
use ash::vk::Handle;

use crate::config::ensure_settings;
use crate::consts::ATTACHMENT_SAMPLE_COUNT_TYPE;
use crate::consts::CHAIN_NODE_REASON;
use crate::consts::CUSTOM_RESOLVE_TYPE;
use crate::consts::DEBUG_UTILS_OBJECT_NAME_TYPE;
use crate::consts::DEVICE_GROUP_PROPERTIES_TYPE;
use crate::consts::DEVICE_GROUP_SIZE;
use crate::consts::DEVICE_GROUP_PRESENT_INFO_TYPE;
use crate::consts::DEVICE_GROUP_SWAPCHAIN_TYPE;
use crate::consts::DISPLAY_PRESENT_INFO_TYPE;
use crate::consts::FRAME_BOUNDARY_TENSORS_TYPE;
use crate::consts::FRAME_BOUNDARY_TYPE;
use crate::consts::PRESENT_ID_2_TYPE;
use crate::consts::PRESENT_ID_TYPE;
use crate::consts::PRESENT_REGIONS_TYPE;
use crate::consts::PRESENT_TIMES_GOOGLE_TYPE;
use crate::consts::PRESENT_TIMINGS_TYPE;
use crate::consts::SET_PRESENT_CONFIG_TYPE;
use crate::consts::SWAPCHAIN_PRESENT_FENCE_TYPE;
use crate::consts::FN_DESTROY_SURFACE;
use crate::consts::FN_DEVICE_GROUPS;
use crate::consts::GRAPHICS_PIPELINE_LIBRARY_TYPE;
use crate::consts::IMAGE_COMPRESSION_CONTROL_TYPE;
use crate::consts::IMAGE_FORMAT_LIST_TYPE;
use crate::consts::IMAGE_USAGE_FLAGS_2_TYPE;
use crate::consts::MULTIVIEW_PER_VIEW_TYPE;
use crate::consts::PIPELINE_BINARY_INFO_TYPE;
use crate::consts::PIPELINE_COMPILER_CONTROL_TYPE;
use crate::consts::PIPELINE_CREATE_FLAGS_2_TYPE;
use crate::consts::PIPELINE_CREATION_FEEDBACK_TYPE;
use crate::consts::PIPELINE_DENSITY_LAYERED_TYPE;
use crate::consts::PIPELINE_DISCARD_RECTANGLE_TYPE;
use crate::consts::PIPELINE_LIBRARY_TYPE;
use crate::consts::PIPELINE_RENDERING_TYPE;
use crate::consts::PIPELINE_REPRESENTATIVE_TYPE;
use crate::consts::PIPELINE_ROBUSTNESS_TYPE;
use crate::consts::PIPELINE_SHADING_RATE_ENUM_TYPE;
use crate::consts::PIPELINE_SHADING_RATE_STATE_TYPE;
use crate::consts::RENDERING_ATTACHMENT_LOCATION_TYPE;
use crate::consts::RENDERING_INPUT_ATTACHMENT_TYPE;
use crate::consts::SHADER_MODULE_CACHE_TYPE;
use crate::consts::SHADER_MODULE_TYPE;
use crate::consts::STAGE_MODULE_IDENTIFIER_TYPE;
use crate::consts::STAGE_SUBGROUP_SIZE_TYPE;
use crate::consts::SWAPCHAIN_COUNTER_TYPE;
use crate::consts::SWAPCHAIN_LATENCY_TYPE;
use crate::consts::SWAPCHAIN_NATIVE_HDR_TYPE;
use crate::consts::SWAPCHAIN_PRESENT_BARRIER_TYPE;
use crate::consts::SWAPCHAIN_PRESENT_SCALING_TYPE;
use crate::consts::VALIDATION_FEATURES_TYPE;
use crate::consts::FN_DEVICE_GROUPS_KHR;
use crate::consts::FN_SURFACE_CAPS_2;
use crate::consts::FN_CREATE_INSTANCE;
use crate::consts::GPU_EMPTY_WARN;
use crate::consts::HOOK_PROVIDERS;
use crate::consts::LOG_INSTANCE_REGISTERED;
use crate::consts::Provider;
use crate::consts::GROUP_EMPTY_WARN;
use crate::consts::SURFACE_CREATORS;
use crate::device::limit_caps;
use crate::env::env_probe_active;
use crate::lists::call_warned;
use crate::lists::filtered;
use crate::lists::kept;
use crate::probe::build_device;
use crate::probe::call_record_device;
use crate::logging::log_at;
use crate::logging::LogLevel;

pub(crate) type PfnSurfaceCaps2 = unsafe extern "system" fn(
    vk::PhysicalDevice,
    *const VkPhysicalDeviceSurfaceInfo2,
    *mut VkSurfaceCapabilities2,
) -> vk::Result;

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkPhysicalDeviceGroupProperties {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) physical_device_count: u32,
    pub(crate) physical_devices: [vk::PhysicalDevice; DEVICE_GROUP_SIZE],
    pub(crate) subset_allocation: vk::Bool32,
}

pub(crate) type PfnDeviceGroups = unsafe extern "system" fn(
    vk::Instance,
    *mut u32,
    *mut VkPhysicalDeviceGroupProperties,
) -> vk::Result;

pub(crate) type PfnCreateSharedSwapchains = unsafe extern "system" fn(
    vk::Device,
    u32,
    *const vk::SwapchainCreateInfoKHR<'_>,
    *const vk::AllocationCallbacks<'_>,
    *mut vk::SwapchainKHR,
) -> vk::Result;

pub(crate) type PfnWriteSamplers = unsafe extern "system" fn(
    vk::Device,
    u32,
    *const vk::SamplerCreateInfo<'_>,
    *const c_void,
) -> vk::Result;

pub(crate) type PfnCmdSetAlphaToCoverage =
    unsafe extern "system" fn(vk::CommandBuffer, vk::Bool32);

pub(crate) type PfnCmdSetAlphaToOne =
    unsafe extern "system" fn(vk::CommandBuffer, vk::Bool32);

pub(crate) type PfnCmdSetDepthClamp =
    unsafe extern "system" fn(vk::CommandBuffer, vk::Bool32);

pub(crate) type PfnGetDeviceQueue2 =
    unsafe extern "system" fn(vk::Device, *const c_void, *mut vk::Queue);

pub(crate) type PfnSetDeviceLoaderData =
    unsafe extern "system" fn(vk::Device, *mut c_void) -> vk::Result;

pub(crate) type PfnCreateSurface = unsafe extern "system" fn(
    vk::Instance,
    *const c_void,
    *const vk::AllocationCallbacks<'_>,
    *mut vk::SurfaceKHR,
) -> vk::Result;

pub(crate) type PfnDestroySurface = unsafe extern "system" fn(
    vk::Instance,
    vk::SurfaceKHR,
    *const vk::AllocationCallbacks<'_>,
);

#[repr(C)]
pub(crate) struct VkLayerLink {
    pub(crate) p_next: *mut VkLayerLink,
    pub(crate) pfn_next_get_instance_proc_addr: vk::PFN_vkGetInstanceProcAddr,
    pub(crate) pfn_next_get_device_proc_addr: vk::PFN_vkGetDeviceProcAddr,
}

pub(crate) struct VkLayerLinkInfo {
    pub(crate) pfn_next_get_instance_proc_addr: vk::PFN_vkGetInstanceProcAddr,
    pub(crate) pfn_next_get_device_proc_addr: vk::PFN_vkGetDeviceProcAddr,
}

#[repr(C)]
pub(crate) struct VkLayerCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) function: i32,
    pub(crate) u_layer_info: *mut VkLayerLink,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkPhysicalDeviceSurfaceInfo2 {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) surface: vk::SurfaceKHR,
}

#[repr(C)]
pub(crate) struct VkSurfaceCapabilities2 {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) surface_capabilities: vk::SurfaceCapabilitiesKHR,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkHandle(pub(crate) u64);

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkChainNode {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkPipelineCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkPipelineBinaryCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) p_keys_and_data_info: *const c_void,
    pub(crate) pipeline: vk::Pipeline,
    pub(crate) p_pipeline_create_info: *const VkPipelineCreateInfoKHR,
}

pub(crate) type PfnGetPipelineKey = unsafe extern "system" fn(
    vk::Device,
    *const VkPipelineCreateInfoKHR,
    *mut c_void,
) -> vk::Result;

pub(crate) type PfnCreatePipelineBinaries = unsafe extern "system" fn(
    vk::Device,
    *const VkPipelineBinaryCreateInfoKHR,
    *const vk::AllocationCallbacks<'_>,
    *mut c_void,
) -> vk::Result;

#[repr(C)]
pub(crate) struct VkDeviceGroupDeviceCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) physical_device_count: u32,
    pub(crate) p_physical_devices: *const vk::PhysicalDevice,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkPhysicalDeviceFeatures2 {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) features: vk::PhysicalDeviceFeatures,
}

#[repr(C)]
pub(crate) struct VkSurfacePresentModeKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) present_mode: vk::PresentModeKHR,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkSwapchainPresentModeInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_present_modes: *const vk::PresentModeKHR,
}

#[repr(C)]
pub(crate) struct VkDeviceGroupPresentInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_device_masks: *const u32,
    pub(crate) mode: vk::Flags,
}

#[repr(C)]
pub(crate) struct VkDisplayPresentInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) src_rect: vk::Rect2D,
    pub(crate) dst_rect: vk::Rect2D,
    pub(crate) persistent: vk::Bool32,
}

#[repr(C)]
pub(crate) struct VkFrameBoundaryEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
    pub(crate) frame_id: u64,
    pub(crate) image_count: u32,
    pub(crate) p_images: *const vk::Image,
    pub(crate) buffer_count: u32,
    pub(crate) p_buffers: *const vk::Buffer,
    pub(crate) tag_name: u64,
    pub(crate) tag_size: usize,
    pub(crate) p_tag: *const c_void,
}

#[repr(C)]
pub(crate) struct VkFrameBoundaryTensorsARM {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) tensor_count: u32,
    pub(crate) p_tensors: *const VkHandle,
}

#[repr(C)]
pub(crate) struct VkPresentId2KHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_present_ids: *const u64,
}

#[repr(C)]
pub(crate) struct VkPresentIdKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_present_ids: *const u64,
}

#[repr(C)]
pub(crate) struct VkPresentRegionsKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_regions: *const c_void,
}

#[repr(C)]
pub(crate) struct VkPresentTimesInfoGOOGLE {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_times: *const c_void,
}

#[repr(C)]
pub(crate) struct VkPresentTimingsInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_timing_infos: *const c_void,
}

#[repr(C)]
pub(crate) struct VkSetPresentConfigNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) num_frames_per_batch: u32,
    pub(crate) present_config_feedback: u32,
}

#[repr(C)]
pub(crate) struct VkSwapchainPresentFenceInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) swapchain_count: u32,
    pub(crate) p_fences: *const vk::Fence,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkPresentModeList {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) present_mode_count: u32,
    pub(crate) p_present_modes: *mut vk::PresentModeKHR,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorMappingSourceConstantOffsetEXT {
    pub(crate) heap_offset: u32,
    pub(crate) heap_array_stride: u32,
    pub(crate) p_embedded_sampler: *const vk::SamplerCreateInfo<'static>,
    pub(crate) sampler_heap_offset: u32,
    pub(crate) sampler_heap_array_stride: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorMappingSourcePushIndexEXT {
    pub(crate) heap_offset: u32,
    pub(crate) push_offset: u32,
    pub(crate) heap_index_stride: u32,
    pub(crate) heap_array_stride: u32,
    pub(crate) p_embedded_sampler: *const vk::SamplerCreateInfo<'static>,
    pub(crate) use_combined_image_sampler_index: vk::Bool32,
    pub(crate) sampler_heap_offset: u32,
    pub(crate) sampler_push_offset: u32,
    pub(crate) sampler_heap_index_stride: u32,
    pub(crate) sampler_heap_array_stride: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorMappingSourceIndirectIndexEXT {
    pub(crate) heap_offset: u32,
    pub(crate) push_offset: u32,
    pub(crate) address_offset: u32,
    pub(crate) heap_index_stride: u32,
    pub(crate) heap_array_stride: u32,
    pub(crate) p_embedded_sampler: *const vk::SamplerCreateInfo<'static>,
    pub(crate) use_combined_image_sampler_index: vk::Bool32,
    pub(crate) sampler_heap_offset: u32,
    pub(crate) sampler_push_offset: u32,
    pub(crate) sampler_address_offset: u32,
    pub(crate) sampler_heap_index_stride: u32,
    pub(crate) sampler_heap_array_stride: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorMappingSourceIndirectIndexArrayEXT {
    pub(crate) heap_offset: u32,
    pub(crate) push_offset: u32,
    pub(crate) address_offset: u32,
    pub(crate) heap_index_stride: u32,
    pub(crate) p_embedded_sampler: *const vk::SamplerCreateInfo<'static>,
    pub(crate) use_combined_image_sampler_index: vk::Bool32,
    pub(crate) sampler_heap_offset: u32,
    pub(crate) sampler_push_offset: u32,
    pub(crate) sampler_address_offset: u32,
    pub(crate) sampler_heap_index_stride: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorMappingSourceShaderRecordIndexEXT {
    pub(crate) heap_offset: u32,
    pub(crate) shader_record_offset: u32,
    pub(crate) heap_index_stride: u32,
    pub(crate) heap_array_stride: u32,
    pub(crate) p_embedded_sampler: *const vk::SamplerCreateInfo<'static>,
    pub(crate) use_combined_image_sampler_index: vk::Bool32,
    pub(crate) sampler_heap_offset: u32,
    pub(crate) sampler_shader_record_offset: u32,
    pub(crate) sampler_heap_index_stride: u32,
    pub(crate) sampler_heap_array_stride: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorMappingSourceHeapDataEXT {
    pub(crate) heap_offset: u32,
    pub(crate) push_offset: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorMappingSourceIndirectAddressEXT {
    pub(crate) push_offset: u32,
    pub(crate) address_offset: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) union VkDescriptorMappingSourceDataEXT {
    pub(crate) constant_offset: VkDescriptorMappingSourceConstantOffsetEXT,
    pub(crate) push_index: VkDescriptorMappingSourcePushIndexEXT,
    pub(crate) indirect_index: VkDescriptorMappingSourceIndirectIndexEXT,
    pub(crate) indirect_index_array: VkDescriptorMappingSourceIndirectIndexArrayEXT,
    pub(crate) heap_data: VkDescriptorMappingSourceHeapDataEXT,
    pub(crate) push_data_offset: u32,
    pub(crate) push_address_offset: u32,
    pub(crate) indirect_address: VkDescriptorMappingSourceIndirectAddressEXT,
    pub(crate) shader_record_index: VkDescriptorMappingSourceShaderRecordIndexEXT,
    pub(crate) shader_record_data_offset: u32,
    pub(crate) shader_record_address_offset: u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkDescriptorSetAndBindingMappingEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) descriptor_set: u32,
    pub(crate) first_binding: u32,
    pub(crate) binding_count: u32,
    pub(crate) resource_mask: vk::Flags,
    pub(crate) source: i32,
    pub(crate) source_data: VkDescriptorMappingSourceDataEXT,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkShaderDescriptorSetAndBindingMappingInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) mapping_count: u32,
    pub(crate) p_mappings: *const VkDescriptorSetAndBindingMappingEXT,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkShaderCreateInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
    pub(crate) stage: vk::Flags,
    pub(crate) next_stage: vk::Flags,
    pub(crate) code_type: i32,
    pub(crate) code_size: usize,
    pub(crate) p_code: *const c_void,
    pub(crate) p_name: *const c_char,
    pub(crate) set_layout_count: u32,
    pub(crate) p_set_layouts: *const vk::DescriptorSetLayout,
    pub(crate) push_constant_range_count: u32,
    pub(crate) p_push_constant_ranges: *const c_void,
    pub(crate) p_specialization_info: *const c_void,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkGraphicsShaderGroupCreateInfoNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) stage_count: u32,
    pub(crate) p_stages: *const vk::PipelineShaderStageCreateInfo<'static>,
    pub(crate) p_vertex_input_state: *const c_void,
    pub(crate) p_tessellation_state: *const c_void,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkGraphicsPipelineShaderGroupsCreateInfoNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) group_count: u32,
    pub(crate) p_groups: *const VkGraphicsShaderGroupCreateInfoNV,
    pub(crate) pipeline_count: u32,
    pub(crate) p_pipelines: *const vk::Pipeline,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkRayTracingPipelineCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
    pub(crate) stage_count: u32,
    pub(crate) p_stages: *const vk::PipelineShaderStageCreateInfo<'static>,
    pub(crate) group_count: u32,
    pub(crate) p_groups: *const c_void,
    pub(crate) max_pipeline_ray_recursion_depth: u32,
    pub(crate) p_library_info: *const c_void,
    pub(crate) p_library_interface: *const c_void,
    pub(crate) p_dynamic_state: *const c_void,
    pub(crate) layout: vk::PipelineLayout,
    pub(crate) base_pipeline_handle: vk::Pipeline,
    pub(crate) base_pipeline_index: i32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkRayTracingPipelineCreateInfoNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
    pub(crate) stage_count: u32,
    pub(crate) p_stages: *const vk::PipelineShaderStageCreateInfo<'static>,
    pub(crate) group_count: u32,
    pub(crate) p_groups: *const c_void,
    pub(crate) max_recursion_depth: u32,
    pub(crate) layout: vk::PipelineLayout,
    pub(crate) base_pipeline_handle: vk::Pipeline,
    pub(crate) base_pipeline_index: i32,
}

pub(crate) type PfnCreateShaders = unsafe extern "system" fn(
    vk::Device,
    u32,
    *const VkShaderCreateInfoEXT,
    *const vk::AllocationCallbacks<'_>,
    *mut VkHandle,
) -> vk::Result;

pub(crate) type PfnCreateRayTracingKHR = unsafe extern "system" fn(
    vk::Device,
    VkHandle,
    vk::PipelineCache,
    u32,
    *const VkRayTracingPipelineCreateInfoKHR,
    *const vk::AllocationCallbacks<'_>,
    *mut vk::Pipeline,
) -> vk::Result;

pub(crate) type PfnCreateRayTracingNV = unsafe extern "system" fn(
    vk::Device,
    vk::PipelineCache,
    u32,
    *const VkRayTracingPipelineCreateInfoNV,
    *const vk::AllocationCallbacks<'_>,
    *mut vk::Pipeline,
) -> vk::Result;

pub(crate) type PfnPipelineIndirectMemory = unsafe extern "system" fn(
    vk::Device,
    *const vk::ComputePipelineCreateInfo<'_>,
    *mut c_void,
);

#[repr(C)]
pub(crate) struct VkDeviceGroupSwapchainCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) modes: vk::Flags,
}

#[repr(C)]
pub(crate) struct VkImageCompressionControlEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
    pub(crate) compression_control_plane_count: u32,
    pub(crate) p_fixed_rate_flags: *mut vk::Flags,
}

#[repr(C)]
pub(crate) struct VkImageFormatListCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) view_format_count: u32,
    pub(crate) p_view_formats: *const vk::Format,
}

#[repr(C)]
pub(crate) struct VkImageUsageFlags2CreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) usage: u64,
}

#[repr(C)]
pub(crate) struct VkSwapchainCounterCreateInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) surface_counters: vk::Flags,
}

#[repr(C)]
pub(crate) struct VkSwapchainDisplayNativeHdrCreateInfoAMD {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) local_dimming_enable: vk::Bool32,
}

#[repr(C)]
pub(crate) struct VkSwapchainLatencyCreateInfoNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) latency_mode_enable: vk::Bool32,
}

#[repr(C)]
pub(crate) struct VkSwapchainPresentBarrierCreateInfoNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *mut c_void,
    pub(crate) present_barrier_enable: vk::Bool32,
}

#[repr(C)]
pub(crate) struct VkSwapchainPresentScalingCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) scaling_behavior: vk::Flags,
    pub(crate) present_gravity_x: vk::Flags,
    pub(crate) present_gravity_y: vk::Flags,
}

#[repr(C)]
pub(crate) struct VkCustomResolveCreateInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) custom_resolve: vk::Bool32,
    pub(crate) color_attachment_count: u32,
    pub(crate) p_color_attachment_formats: *const vk::Format,
    pub(crate) depth_attachment_format: vk::Format,
    pub(crate) stencil_attachment_format: vk::Format,
}

#[repr(C)]
pub(crate) struct VkDebugUtilsObjectNameInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) object_type: i32,
    pub(crate) object_handle: u64,
    pub(crate) p_object_name: *const c_char,
}

#[repr(C)]
pub(crate) struct VkPipelineRobustnessCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) storage_buffers: i32,
    pub(crate) uniform_buffers: i32,
    pub(crate) vertex_inputs: i32,
    pub(crate) images: i32,
}

#[repr(C)]
pub(crate) struct VkPipelineShaderStageModuleIdentifierCreateInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) identifier_size: u32,
    pub(crate) p_identifier: *const u8,
}

#[repr(C)]
pub(crate) struct VkPipelineShaderStageRequiredSubgroupSizeCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) required_subgroup_size: u32,
}

#[repr(C)]
pub(crate) struct VkShaderModuleCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
    pub(crate) code_size: usize,
    pub(crate) p_code: *const u32,
}

#[repr(C)]
pub(crate) struct VkShaderModuleValidationCacheCreateInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) validation_cache: VkHandle,
}

#[repr(C)]
pub(crate) struct VkValidationFeaturesEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) enabled_validation_feature_count: u32,
    pub(crate) p_enabled_validation_features: *const i32,
    pub(crate) disabled_validation_feature_count: u32,
    pub(crate) p_disabled_validation_features: *const i32,
}

#[repr(C)]
pub(crate) struct VkAttachmentSampleCountInfoAMD {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) color_attachment_count: u32,
    pub(crate) p_color_attachment_samples: *const vk::Flags,
    pub(crate) depth_stencil_attachment_samples: vk::Flags,
}

#[repr(C)]
pub(crate) struct VkGraphicsPipelineLibraryCreateInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
}

#[repr(C)]
pub(crate) struct VkMultiviewPerViewAttributesInfoNVX {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) per_view_attributes: vk::Bool32,
    pub(crate) per_view_attributes_position_x_only: vk::Bool32,
}

#[repr(C)]
pub(crate) struct VkPipelineBinaryInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) binary_count: u32,
    pub(crate) p_pipeline_binaries: *const VkHandle,
}

#[repr(C)]
pub(crate) struct VkPipelineCompilerControlCreateInfoAMD {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) compiler_control_flags: vk::Flags,
}

#[repr(C)]
pub(crate) struct VkPipelineCreateFlags2CreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: u64,
}

#[repr(C)]
pub(crate) struct VkPipelineCreationFeedbackCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) p_pipeline_creation_feedback: *mut c_void,
    pub(crate) pipeline_stage_creation_feedback_count: u32,
    pub(crate) p_pipeline_stage_creation_feedbacks: *mut c_void,
}

#[repr(C)]
pub(crate) struct VkPipelineDiscardRectangleStateCreateInfoEXT {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) flags: vk::Flags,
    pub(crate) discard_rectangle_mode: i32,
    pub(crate) discard_rectangle_count: u32,
    pub(crate) p_discard_rectangles: *const vk::Rect2D,
}

#[repr(C)]
pub(crate) struct VkPipelineFragmentDensityMapLayeredCreateInfoVALVE {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) max_fragment_density_map_layers: u32,
}

#[repr(C)]
pub(crate) struct VkPipelineFragmentShadingRateEnumStateCreateInfoNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) shading_rate_type: i32,
    pub(crate) shading_rate: i32,
    pub(crate) combiner_ops: [i32; 2],
}

#[repr(C)]
pub(crate) struct VkPipelineFragmentShadingRateStateCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) fragment_size: vk::Extent2D,
    pub(crate) combiner_ops: [i32; 2],
}

#[repr(C)]
pub(crate) struct VkPipelineLibraryCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) library_count: u32,
    pub(crate) p_libraries: *const vk::Pipeline,
}

#[repr(C)]
pub(crate) struct VkPipelineRenderingCreateInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) view_mask: u32,
    pub(crate) color_attachment_count: u32,
    pub(crate) p_color_attachment_formats: *const vk::Format,
    pub(crate) depth_attachment_format: vk::Format,
    pub(crate) stencil_attachment_format: vk::Format,
}

#[repr(C)]
pub(crate) struct VkPipelineRepresentativeFragmentTestStateCreateInfoNV {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) representative_fragment_test_enable: vk::Bool32,
}

#[repr(C)]
pub(crate) struct VkRenderingAttachmentLocationInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) color_attachment_count: u32,
    pub(crate) p_color_attachment_locations: *const u32,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct VkSwapchainPresentModesCreateInfoKHR {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) present_mode_count: u32,
    pub(crate) p_present_modes: *const vk::PresentModeKHR,
}

#[repr(C)]
pub(crate) struct VkRenderingInputAttachmentIndexInfo {
    pub(crate) s_type: vk::StructureType,
    pub(crate) p_next: *const c_void,
    pub(crate) color_attachment_count: u32,
    pub(crate) p_color_attachment_input_indices: *const u32,
    pub(crate) p_depth_input_attachment_index: *const u32,
    pub(crate) p_stencil_input_attachment_index: *const u32,
}

#[derive(Clone)]
pub(crate) struct VkInstState {
    pub(crate) instance: ash::Instance,
    pub(crate) gipa: vk::PFN_vkGetInstanceProcAddr,
    pub(crate) surface_fp: ash::khr::surface::InstanceFn,
    pub(crate) caps2_fp: Option<PfnSurfaceCaps2>,
    pub(crate) groups_fp: Option<PfnDeviceGroups>,
    pub(crate) groups_khr_fp: Option<PfnDeviceGroups>,
    pub(crate) surface_fps: HashMap<&'static str, PfnCreateSurface>,
    pub(crate) destroy_surface_fp: Option<PfnDestroySurface>,
    pub(crate) api_version: u32,
    pub(crate) extensions: Arc<HashSet<String>>,
}

pub(crate) fn provider_on(api_version: u32, extensions: &HashSet<String>, command: &str) -> bool {
    HOOK_PROVIDERS
        .iter()
        .filter(|(name, _)| *name == command)
        .any(|(_, provider)| match provider {
            Provider::Version(least) => api_version >= *least,
            Provider::Ext(name) => extensions.contains(*name),
        })
}

pub(crate) fn cstr_names(names: *const *const c_char, count: u32) -> HashSet<String> {
    (0..count as usize)
        .map(|at| {
            unsafe { CStr::from_ptr(*names.add(at)) }
                .to_string_lossy()
                .into_owned()
        })
        .collect()
}

static INSTS: RwLock<Option<HashMap<u64, VkInstState>>> = RwLock::new(None);
static PHYS_OWNER: RwLock<Option<HashMap<u64, u64>>> = RwLock::new(None);
static SURFACE_TAGS: RwLock<Option<HashMap<(u64, u64), &'static str>>> = RwLock::new(None);

fn phys_owner_get(phys: u64) -> Option<u64> {
    PHYS_OWNER
        .read()
        .ok()
        .and_then(|g| g.as_ref().and_then(|m| m.get(&phys).copied()))
}

fn phys_owner_put(phys: u64, inst: u64) {
    match PHYS_OWNER.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(phys, inst);
        }
        Err(_) => (),
    }
}

fn phys_owner_forget(inst: u64) {
    match PHYS_OWNER.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|_, owner| *owner != inst)),
        Err(_) => (),
    }
}

pub(crate) fn insts_get(h: u64) -> Option<VkInstState> {
    INSTS.read().ok().and_then(|g| g.as_ref().and_then(|m| m.get(&h).cloned()))
}

pub(crate) fn insts_put(h: u64, v: VkInstState) {
    match INSTS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert(h, v);
        }
        Err(_) => (),
    }
}

pub(crate) fn insts_del(h: u64) {
    phys_owner_forget(h);
    surface_tags_forget(h);
    match INSTS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).remove(&h);
        }
        Err(_) => (),
    }
}

pub(crate) fn owning_instance(phys: vk::PhysicalDevice) -> Option<(u64, VkInstState)> {
    phys_owner_get(phys.as_raw()).and_then(|h| insts_get(h).map(|st| (h, st)))
}

fn surface_tag_put(inst: u64, surface: u64, tag: &'static str) {
    match SURFACE_TAGS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).insert((inst, surface), tag);
        }
        Err(_) => (),
    }
}

fn surface_tag_del(inst: u64, surface: u64) {
    match SURFACE_TAGS.write() {
        Ok(mut g) => {
            g.get_or_insert_with(HashMap::new).remove(&(inst, surface));
        }
        Err(_) => (),
    }
}

fn surface_tags_forget(inst: u64) {
    match SURFACE_TAGS.write() {
        Ok(mut g) => g
            .iter_mut()
            .for_each(|m| m.retain(|(owner, _), _| *owner != inst)),
        Err(_) => (),
    }
}

pub(crate) fn surface_tag(inst: vk::Instance, surface: vk::SurfaceKHR) -> Option<&'static str> {
    SURFACE_TAGS.read().ok().and_then(|g| {
        g.as_ref()
            .and_then(|m| m.get(&(inst.as_raw(), surface.as_raw())).copied())
    })
}

fn call_tagged_result(
    result: vk::Result,
    inst: vk::Instance,
    tag: &'static str,
    out: *mut vk::SurfaceKHR,
) -> vk::Result {
    match result {
        vk::Result::SUCCESS => {
            surface_tag_put(inst.as_raw(), unsafe { (*out).as_raw() }, tag);
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_create_tagged_surface(
    name: &'static str,
    tag: &'static str,
    inst: vk::Instance,
    ci: *const c_void,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::SurfaceKHR,
) -> vk::Result {
    match insts_get(inst.as_raw()).and_then(|st| st.surface_fps.get(name).copied()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(fp) => call_tagged_result(unsafe { fp(inst, ci, alloc, out) }, inst, tag, out),
    }
}

pub(crate) fn call_destroy_tagged_surface(
    inst: vk::Instance,
    surface: vk::SurfaceKHR,
    alloc: *const vk::AllocationCallbacks<'_>,
) {
    surface_tag_del(inst.as_raw(), surface.as_raw());
    match insts_get(inst.as_raw()).and_then(|st| st.destroy_surface_fp) {
        Some(fp) => unsafe { fp(inst, surface, alloc) },
        None => (),
    }
}

pub(crate) fn all_devices(inst: &VkInstState) -> Vec<vk::PhysicalDevice> {
    call_owned_devices(&inst.instance)
}

pub(crate) fn device_index(all: &[vk::PhysicalDevice], phys: vk::PhysicalDevice) -> u32 {
    all.iter()
        .position(|device| *device == phys)
        .map(|at| at as u32 + 1)
        .unwrap_or(1)
}

fn indexed(devices: Vec<vk::PhysicalDevice>) -> Vec<(usize, vk::PhysicalDevice)> {
    devices.into_iter().enumerate().collect()
}

fn plain(pairs: Vec<(usize, vk::PhysicalDevice)>) -> Vec<vk::PhysicalDevice> {
    pairs.into_iter().map(|(_, device)| device).collect()
}

fn device_position(pair: &(usize, vk::PhysicalDevice)) -> u32 {
    pair.0 as u32 + 1
}

fn call_gpu_filtered(
    devices: Vec<vk::PhysicalDevice>,
    choice: Option<u32>,
) -> Vec<vk::PhysicalDevice> {
    plain(call_warned(
        filtered(indexed(devices), choice, |pair| Some(device_position(pair))),
        GPU_EMPTY_WARN,
    ))
}

fn group_devices(group: &VkPhysicalDeviceGroupProperties) -> Vec<vk::PhysicalDevice> {
    group.physical_devices[..group.physical_device_count as usize].to_vec()
}

fn subset_of(kept_count: usize, original: vk::Bool32) -> vk::Bool32 {
    match kept_count {
        1 => vk::FALSE,
        _ => original,
    }
}

fn narrowed_group(
    group: VkPhysicalDeviceGroupProperties,
    allowed: &[vk::PhysicalDevice],
) -> VkPhysicalDeviceGroupProperties {
    let held: Vec<vk::PhysicalDevice> = group_devices(&group)
        .into_iter()
        .filter(|device| allowed.contains(device))
        .collect();
    let mut narrowed = group;
    narrowed.physical_device_count = held.len() as u32;
    (0..held.len()).for_each(|at| narrowed.physical_devices[at] = held[at]);
    narrowed.subset_allocation = subset_of(held.len(), group.subset_allocation);
    narrowed
}

fn call_group_filtered(
    groups: Vec<VkPhysicalDeviceGroupProperties>,
    allowed: Vec<vk::PhysicalDevice>,
    choice: Option<u32>,
) -> Vec<VkPhysicalDeviceGroupProperties> {
    match choice {
        Some(_) => call_warned(
            kept(
                groups
                    .into_iter()
                    .map(|group| narrowed_group(group, &allowed))
                    .collect(),
                |group| group.physical_device_count > 0,
            ),
            GROUP_EMPTY_WARN,
        ),
        None => groups,
    }
}

fn copy_count(requested: u32, available: usize) -> usize {
    (requested as usize).min(available)
}

fn completeness(written: usize, available: usize) -> vk::Result {
    match written == available {
        true => vk::Result::SUCCESS,
        false => vk::Result::INCOMPLETE,
    }
}

fn non_null_ci(p: *const VkLayerCreateInfo) -> Option<*const VkLayerCreateInfo> {
    match p.is_null() {
        true => None,
        false => Some(p),
    }
}

pub(crate) fn chain_layer_info(
    p_next: *const c_void,
    want: u32,
    function: i32,
) -> *mut VkLayerCreateInfo {
    std::iter::successors(non_null_ci(p_next as *const VkLayerCreateInfo), |p| {
        non_null_ci(unsafe { (**p).p_next as *const VkLayerCreateInfo })
    })
    .find(|p| unsafe { (**p).s_type.as_raw() as u32 == want && (**p).function == function })
    .map(|p| p as *mut VkLayerCreateInfo)
    .unwrap_or(ptr::null_mut())
}

pub(crate) struct Relinked {
    pub(crate) head: *const c_void,
    #[allow(dead_code)]
    pub(crate) blocks: Vec<Vec<u64>>,
}

fn block_words<T>() -> usize {
    mem::size_of::<T>().div_ceil(mem::size_of::<u64>()).max(1)
}

fn copied<T>(node: *const VkChainNode) -> Vec<u64> {
    let mut block = vec![0u64; block_words::<T>()];
    unsafe { ptr::write(block.as_mut_ptr() as *mut T, ptr::read(node as *const T)) };
    block
}

pub(crate) fn copied_node(node: *const VkChainNode) -> Option<Vec<u64>> {
    match chain_node_type(node) {
        DEVICE_GROUP_SWAPCHAIN_TYPE => Some(copied::<VkDeviceGroupSwapchainCreateInfoKHR>(node)),
        IMAGE_COMPRESSION_CONTROL_TYPE => Some(copied::<VkImageCompressionControlEXT>(node)),
        IMAGE_FORMAT_LIST_TYPE => Some(copied::<VkImageFormatListCreateInfo>(node)),
        IMAGE_USAGE_FLAGS_2_TYPE => Some(copied::<VkImageUsageFlags2CreateInfoKHR>(node)),
        SWAPCHAIN_COUNTER_TYPE => Some(copied::<VkSwapchainCounterCreateInfoEXT>(node)),
        SWAPCHAIN_NATIVE_HDR_TYPE => Some(copied::<VkSwapchainDisplayNativeHdrCreateInfoAMD>(node)),
        SWAPCHAIN_LATENCY_TYPE => Some(copied::<VkSwapchainLatencyCreateInfoNV>(node)),
        SWAPCHAIN_PRESENT_BARRIER_TYPE => Some(copied::<VkSwapchainPresentBarrierCreateInfoNV>(node)),
        SWAPCHAIN_PRESENT_SCALING_TYPE => Some(copied::<VkSwapchainPresentScalingCreateInfoKHR>(node)),
        CUSTOM_RESOLVE_TYPE => Some(copied::<VkCustomResolveCreateInfoEXT>(node)),
        DEBUG_UTILS_OBJECT_NAME_TYPE => Some(copied::<VkDebugUtilsObjectNameInfoEXT>(node)),
        PIPELINE_ROBUSTNESS_TYPE => Some(copied::<VkPipelineRobustnessCreateInfo>(node)),
        STAGE_MODULE_IDENTIFIER_TYPE => Some(copied::<VkPipelineShaderStageModuleIdentifierCreateInfoEXT>(node)),
        STAGE_SUBGROUP_SIZE_TYPE => Some(copied::<VkPipelineShaderStageRequiredSubgroupSizeCreateInfo>(node)),
        SHADER_MODULE_TYPE => Some(copied::<VkShaderModuleCreateInfo>(node)),
        SHADER_MODULE_CACHE_TYPE => Some(copied::<VkShaderModuleValidationCacheCreateInfoEXT>(node)),
        VALIDATION_FEATURES_TYPE => Some(copied::<VkValidationFeaturesEXT>(node)),
        ATTACHMENT_SAMPLE_COUNT_TYPE => Some(copied::<VkAttachmentSampleCountInfoAMD>(node)),
        GRAPHICS_PIPELINE_LIBRARY_TYPE => Some(copied::<VkGraphicsPipelineLibraryCreateInfoEXT>(node)),
        MULTIVIEW_PER_VIEW_TYPE => Some(copied::<VkMultiviewPerViewAttributesInfoNVX>(node)),
        PIPELINE_BINARY_INFO_TYPE => Some(copied::<VkPipelineBinaryInfoKHR>(node)),
        PIPELINE_COMPILER_CONTROL_TYPE => Some(copied::<VkPipelineCompilerControlCreateInfoAMD>(node)),
        PIPELINE_CREATE_FLAGS_2_TYPE => Some(copied::<VkPipelineCreateFlags2CreateInfo>(node)),
        PIPELINE_CREATION_FEEDBACK_TYPE => Some(copied::<VkPipelineCreationFeedbackCreateInfo>(node)),
        PIPELINE_DISCARD_RECTANGLE_TYPE => Some(copied::<VkPipelineDiscardRectangleStateCreateInfoEXT>(node)),
        PIPELINE_DENSITY_LAYERED_TYPE => Some(copied::<VkPipelineFragmentDensityMapLayeredCreateInfoVALVE>(node)),
        PIPELINE_SHADING_RATE_ENUM_TYPE => Some(copied::<VkPipelineFragmentShadingRateEnumStateCreateInfoNV>(node)),
        PIPELINE_SHADING_RATE_STATE_TYPE => Some(copied::<VkPipelineFragmentShadingRateStateCreateInfoKHR>(node)),
        PIPELINE_LIBRARY_TYPE => Some(copied::<VkPipelineLibraryCreateInfoKHR>(node)),
        PIPELINE_RENDERING_TYPE => Some(copied::<VkPipelineRenderingCreateInfo>(node)),
        PIPELINE_REPRESENTATIVE_TYPE => Some(copied::<VkPipelineRepresentativeFragmentTestStateCreateInfoNV>(node)),
        RENDERING_ATTACHMENT_LOCATION_TYPE => Some(copied::<VkRenderingAttachmentLocationInfo>(node)),
        RENDERING_INPUT_ATTACHMENT_TYPE => Some(copied::<VkRenderingInputAttachmentIndexInfo>(node)),
        DEVICE_GROUP_PRESENT_INFO_TYPE => Some(copied::<VkDeviceGroupPresentInfoKHR>(node)),
        DISPLAY_PRESENT_INFO_TYPE => Some(copied::<VkDisplayPresentInfoKHR>(node)),
        FRAME_BOUNDARY_TYPE => Some(copied::<VkFrameBoundaryEXT>(node)),
        FRAME_BOUNDARY_TENSORS_TYPE => Some(copied::<VkFrameBoundaryTensorsARM>(node)),
        PRESENT_ID_2_TYPE => Some(copied::<VkPresentId2KHR>(node)),
        PRESENT_ID_TYPE => Some(copied::<VkPresentIdKHR>(node)),
        PRESENT_REGIONS_TYPE => Some(copied::<VkPresentRegionsKHR>(node)),
        PRESENT_TIMES_GOOGLE_TYPE => Some(copied::<VkPresentTimesInfoGOOGLE>(node)),
        PRESENT_TIMINGS_TYPE => Some(copied::<VkPresentTimingsInfoEXT>(node)),
        SET_PRESENT_CONFIG_TYPE => Some(copied::<VkSetPresentConfigNV>(node)),
        SWAPCHAIN_PRESENT_FENCE_TYPE => Some(copied::<VkSwapchainPresentFenceInfoKHR>(node)),
        _ => None,
    }
}

fn const_node(p: *const c_void) -> Option<*const VkChainNode> {
    match p.is_null() {
        true => None,
        false => Some(p as *const VkChainNode),
    }
}

fn mut_node(p: *mut c_void) -> Option<*mut VkChainNode> {
    match p.is_null() {
        true => None,
        false => Some(p as *mut VkChainNode),
    }
}

pub(crate) fn walked_nodes(head: *const c_void) -> Vec<*const VkChainNode> {
    std::iter::successors(const_node(head), |node| {
        const_node(unsafe { (**node).p_next })
    })
    .collect()
}

pub(crate) fn filled_nodes(head: *mut c_void) -> Vec<*mut VkChainNode> {
    std::iter::successors(mut_node(head), |node| mut_node(unsafe { (**node).p_next }))
        .collect()
}

fn chain_node_type(node: *const VkChainNode) -> u32 {
    unsafe { (*node).s_type.as_raw() as u32 }
}

pub(crate) fn chain_find(head: *const c_void, want: u32) -> Option<*const VkChainNode> {
    walked_nodes(head)
        .into_iter()
        .find(|node| chain_node_type(*node) == want)
}

fn nodes_in_front(head: *const c_void, want: u32) -> Vec<*const VkChainNode> {
    walked_nodes(head)
        .into_iter()
        .take_while(|node| chain_node_type(*node) != want)
        .collect()
}

fn copied_nodes(front: Vec<*const VkChainNode>) -> Option<Vec<Vec<u64>>> {
    front.into_iter().map(copied_node).collect()
}

fn chained_blocks(blocks: &mut Vec<Vec<u64>>, tail: *const c_void) -> *const c_void {
    (0..blocks.len()).rev().fold(tail, |next, at| {
        unsafe { (*(blocks[at].as_mut_ptr() as *mut VkChainNode)).p_next = next as *mut c_void };
        blocks[at].as_ptr() as *const c_void
    })
}

fn relinked_from(mut blocks: Vec<Vec<u64>>, replacement: *const c_void) -> Relinked {
    let head = chained_blocks(&mut blocks, replacement);
    Relinked { head, blocks }
}

pub(crate) fn relinked_chain(
    head: *const c_void,
    target: u32,
    replacement: *const c_void,
) -> Option<Relinked> {
    copied_nodes(nodes_in_front(head, target)).map(|blocks| relinked_from(blocks, replacement))
}

pub(crate) fn call_relinked_chain(
    head: *const c_void,
    target: u32,
    replacement: *const c_void,
    setting: &'static str,
) -> Option<Relinked> {
    match relinked_chain(head, target, replacement) {
        Some(built) => Some(built),
        None => {
            log_at(
                LogLevel::Warn,
                &format!("{}: {}", setting, CHAIN_NODE_REASON),
            );
            None
        }
    }
}

pub(crate) fn call_loader_data_fn(node: *mut VkLayerCreateInfo) -> Option<PfnSetDeviceLoaderData> {
    unsafe { node.as_ref() }
        .map(|info| info.u_layer_info)
        .filter(|link| !link.is_null())
        .map(|link| unsafe { mem::transmute(link) })
}

pub(crate) fn call_advance_chain(link: *mut VkLayerCreateInfo) -> Option<VkLayerLinkInfo> {
    match link.is_null() || unsafe { (*link).u_layer_info.is_null() } {
        true => None,
        false => unsafe {
            let li = (*link).u_layer_info;
            let out = VkLayerLinkInfo {
                pfn_next_get_instance_proc_addr: (*li).pfn_next_get_instance_proc_addr,
                pfn_next_get_device_proc_addr: (*li).pfn_next_get_device_proc_addr,
            };
            (*link).u_layer_info = (*li).p_next;
            Some(out)
        },
    }
}

pub(crate) fn call_next_gipa(gipa: vk::PFN_vkGetInstanceProcAddr, inst: vk::Instance, name: &str) -> vk::PFN_vkVoidFunction {
    let c = CString::new(name).unwrap_or_default();
    unsafe { gipa(inst, c.as_ptr()) }
}

pub(crate) fn call_next_gdpa(gdpa: vk::PFN_vkGetDeviceProcAddr, dev: vk::Device, name: &str) -> vk::PFN_vkVoidFunction {
    let c = CString::new(name).unwrap_or_default();
    unsafe { gdpa(dev, c.as_ptr()) }
}

fn call_write_count<T>(list: &[T], count: *mut u32) -> vk::Result {
    unsafe { *count = list.len() as u32 };
    vk::Result::SUCCESS
}

fn call_write_items<T: Copy>(list: &[T], count: *mut u32, out: *mut T) -> vk::Result {
    let n = copy_count(unsafe { *count }, list.len());
    (0..n).for_each(|i| unsafe { *out.add(i) = list[i] });
    unsafe { *count = n as u32 };
    completeness(n, list.len())
}

pub(crate) fn call_write_list<T: Copy>(list: &[T], count: *mut u32, out: *mut T) -> vk::Result {
    match out.is_null() {
        true => call_write_count(list, count),
        false => call_write_items(list, count, out),
    }
}

fn call_enumerate_through(
    st: &VkInstState,
    count: *mut u32,
    devices: *mut vk::PhysicalDevice,
) -> vk::Result {
    match unsafe { st.instance.enumerate_physical_devices() } {
        Ok(all) => call_write_list(&call_gpu_filtered(all, ensure_settings().gpu), count, devices),
        Err(e) => e,
    }
}

pub(crate) fn call_filtered_enumerate(
    inst: vk::Instance,
    count: *mut u32,
    devices: *mut vk::PhysicalDevice,
) -> vk::Result {
    match insts_get(inst.as_raw()) {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(st) => call_enumerate_through(&st, count, devices),
    }
}

fn empty_group() -> VkPhysicalDeviceGroupProperties {
    VkPhysicalDeviceGroupProperties {
        s_type: vk::StructureType::from_raw(DEVICE_GROUP_PROPERTIES_TYPE as i32),
        p_next: ptr::null_mut(),
        physical_device_count: 0,
        physical_devices: [vk::PhysicalDevice::null(); DEVICE_GROUP_SIZE],
        subset_allocation: vk::FALSE,
    }
}

fn call_query_groups(
    handle: vk::Instance,
    fp: PfnDeviceGroups,
) -> Vec<VkPhysicalDeviceGroupProperties> {
    let mut n: u32 = 0;
    let r1 = unsafe { fp(handle, &mut n, ptr::null_mut()) };
    let mut v: Vec<VkPhysicalDeviceGroupProperties> =
        (0..n).map(|_| empty_group()).collect();
    let r2 = unsafe { fp(handle, &mut n, v.as_mut_ptr()) };
    match (r1, r2) {
        (vk::Result::SUCCESS, vk::Result::SUCCESS) => v.into_iter().take(n as usize).collect(),
        (vk::Result::SUCCESS, vk::Result::INCOMPLETE) => call_query_groups(handle, fp),
        (_, _) => Vec::new(),
    }
}

fn call_allowed_devices(st: &VkInstState) -> Vec<vk::PhysicalDevice> {
    call_gpu_filtered(all_devices(st), ensure_settings().gpu)
}

fn call_groups_through(
    st: &VkInstState,
    handle: vk::Instance,
    fp: PfnDeviceGroups,
    count: *mut u32,
    groups: *mut VkPhysicalDeviceGroupProperties,
) -> vk::Result {
    call_write_list(
        &call_group_filtered(
            call_query_groups(handle, fp),
            call_allowed_devices(st),
            ensure_settings().gpu,
        ),
        count,
        groups,
    )
}

fn call_groups_with(
    inst: vk::Instance,
    found: Option<(VkInstState, PfnDeviceGroups)>,
    count: *mut u32,
    groups: *mut VkPhysicalDeviceGroupProperties,
) -> vk::Result {
    match found {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some((st, fp)) => call_groups_through(&st, inst, fp, count, groups),
    }
}

pub(crate) fn call_filtered_groups(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut VkPhysicalDeviceGroupProperties,
) -> vk::Result {
    call_groups_with(
        inst,
        insts_get(inst.as_raw()).and_then(|st| st.groups_fp.map(|fp| (st, fp))),
        count,
        groups,
    )
}

pub(crate) fn call_filtered_groups_khr(
    inst: vk::Instance,
    count: *mut u32,
    groups: *mut VkPhysicalDeviceGroupProperties,
) -> vk::Result {
    call_groups_with(
        inst,
        insts_get(inst.as_raw()).and_then(|st| st.groups_khr_fp.map(|fp| (st, fp))),
        count,
        groups,
    )
}

fn load_surface_fp(
    gipa: vk::PFN_vkGetInstanceProcAddr,
    handle: vk::Instance,
) -> ash::khr::surface::InstanceFn {
    ash::khr::surface::InstanceFn::load(|name| unsafe {
        mem::transmute(gipa(handle, name.as_ptr()))
    })
}

fn call_typed_instance_fp<T>(
    gipa: vk::PFN_vkGetInstanceProcAddr,
    handle: vk::Instance,
    name: &str,
) -> Option<T> {
    call_next_gipa(gipa, handle, name).map(|f| unsafe { mem::transmute_copy(&f) })
}

fn call_owned_devices(instance: &ash::Instance) -> Vec<vk::PhysicalDevice> {
    unsafe { instance.enumerate_physical_devices() }.unwrap_or_default()
}

fn call_probe_first_device(st: &VkInstState, phys: vk::PhysicalDevice) {
    let props = unsafe { st.instance.get_physical_device_properties(phys) };
    call_record_device(build_device(st, phys, &limit_caps(&props)));
}

fn call_probe_devices(st: &VkInstState) {
    match (env_probe_active(), call_allowed_devices(st).first().copied()) {
        (true, Some(phys)) => call_probe_first_device(st, phys),
        (_, _) => (),
    }
}

fn call_remember_owner(handle: vk::Instance, devices: Vec<vk::PhysicalDevice>) {
    devices
        .into_iter()
        .for_each(|phys| phys_owner_put(phys.as_raw(), handle.as_raw()));
}

fn call_surface_creators(
    gipa: vk::PFN_vkGetInstanceProcAddr,
    handle: vk::Instance,
) -> HashMap<&'static str, PfnCreateSurface> {
    SURFACE_CREATORS
        .iter()
        .filter_map(|(name, _)| {
            call_typed_instance_fp::<PfnCreateSurface>(gipa, handle, name).map(|fp| (*name, fp))
        })
        .collect()
}

fn requested_api_version(ci: *const vk::InstanceCreateInfo<'_>) -> u32 {
    match unsafe { (*ci).p_application_info.as_ref() } {
        None => vk::API_VERSION_1_0,
        Some(info) => match info.api_version {
            0 => vk::API_VERSION_1_0,
            asked => asked,
        },
    }
}

fn requested_instance_extensions(ci: *const vk::InstanceCreateInfo<'_>) -> HashSet<String> {
    cstr_names(unsafe { (*ci).pp_enabled_extension_names }, unsafe {
        (*ci).enabled_extension_count
    })
}

fn register_instance(
    gipa: vk::PFN_vkGetInstanceProcAddr,
    handle: vk::Instance,
    api_version: u32,
    extensions: HashSet<String>,
) {
    let static_fn = ash::StaticFn { get_instance_proc_addr: gipa };
    let instance = unsafe { ash::Instance::load(&static_fn, handle) };
    let devices = call_owned_devices(&instance);
    call_remember_owner(handle, devices);
    let state = VkInstState {
            instance,
            gipa,
            surface_fp: load_surface_fp(gipa, handle),
            caps2_fp: call_typed_instance_fp(gipa, handle, FN_SURFACE_CAPS_2),
            groups_fp: call_typed_instance_fp(gipa, handle, FN_DEVICE_GROUPS),
            groups_khr_fp: call_typed_instance_fp(gipa, handle, FN_DEVICE_GROUPS_KHR),
            surface_fps: call_surface_creators(gipa, handle),
            destroy_surface_fp: call_typed_instance_fp(gipa, handle, FN_DESTROY_SURFACE),
            api_version,
            extensions: Arc::new(extensions),
    };
    call_probe_devices(&state);
    insts_put(handle.as_raw(), state);
    log_at(LogLevel::Info, LOG_INSTANCE_REGISTERED);
}

fn invoke_create_instance(
    create_fn: unsafe extern "system" fn(),
    gipa: vk::PFN_vkGetInstanceProcAddr,
    ci: *const vk::InstanceCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Instance,
) -> vk::Result {
    match unsafe {
        let cf: vk::PFN_vkCreateInstance = mem::transmute(create_fn);
        cf(ci, alloc, out)
    } {
        vk::Result::SUCCESS => {
            register_instance(
                gipa,
                unsafe { *out },
                requested_api_version(ci),
                requested_instance_extensions(ci),
            );
            vk::Result::SUCCESS
        }
        e => e,
    }
}

pub(crate) fn call_real_create_instance(
    link: Option<VkLayerLinkInfo>,
    ci: *const vk::InstanceCreateInfo<'_>,
    alloc: *const vk::AllocationCallbacks<'_>,
    out: *mut vk::Instance,
) -> vk::Result {
    match link {
        None => vk::Result::ERROR_INITIALIZATION_FAILED,
        Some(l) => call_next_gipa(l.pfn_next_get_instance_proc_addr, vk::Instance::null(), FN_CREATE_INSTANCE)
            .map(|f| invoke_create_instance(f, l.pfn_next_get_instance_proc_addr, ci, alloc, out))
            .unwrap_or(vk::Result::ERROR_INITIALIZATION_FAILED),
    }
}
