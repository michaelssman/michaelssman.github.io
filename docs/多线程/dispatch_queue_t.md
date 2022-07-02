## dispatch_queue_create

```c
dispatch_queue_t
dispatch_queue_create(const char *label, dispatch_queue_attr_t attr)
{
	return _dispatch_lane_create_with_target(label, attr,
			DISPATCH_TARGET_QUEUE_DEFAULT, true);
}
```

```c
DISPATCH_NOINLINE
static dispatch_queue_t
_dispatch_lane_create_with_target(const char *label, dispatch_queue_attr_t dqa,
		dispatch_queue_t tq, bool legacy)
{
	dispatch_queue_attr_info_t dqai = _dispatch_queue_attr_to_info(dqa);

	//
	// Step 1: Normalize arguments (qos, overcommit, tq)
	//

	dispatch_qos_t qos = dqai.dqai_qos;
#if !HAVE_PTHREAD_WORKQUEUE_QOS
	if (qos == DISPATCH_QOS_USER_INTERACTIVE) {
		dqai.dqai_qos = qos = DISPATCH_QOS_USER_INITIATED;
	}
	if (qos == DISPATCH_QOS_MAINTENANCE) {
		dqai.dqai_qos = qos = DISPATCH_QOS_BACKGROUND;
	}
#endif // !HAVE_PTHREAD_WORKQUEUE_QOS

	_dispatch_queue_attr_overcommit_t overcommit = dqai.dqai_overcommit;
	if (overcommit != _dispatch_queue_attr_overcommit_unspecified && tq) {
		if (tq->do_targetq) {
			DISPATCH_CLIENT_CRASH(tq, "Cannot specify both overcommit and "
					"a non-global target queue");
		}
	}

	if (tq && dx_type(tq) == DISPATCH_QUEUE_GLOBAL_ROOT_TYPE) {
		// Handle discrepancies between attr and target queue, attributes win
		if (overcommit == _dispatch_queue_attr_overcommit_unspecified) {
			if (tq->dq_priority & DISPATCH_PRIORITY_FLAG_OVERCOMMIT) {
				overcommit = _dispatch_queue_attr_overcommit_enabled;
			} else {
				overcommit = _dispatch_queue_attr_overcommit_disabled;
			}
		}
		if (qos == DISPATCH_QOS_UNSPECIFIED) {
			qos = _dispatch_priority_qos(tq->dq_priority);
		}
		tq = NULL;
	} else if (tq && !tq->do_targetq) {
		// target is a pthread or runloop root queue, setting QoS or overcommit
		// is disallowed
		if (overcommit != _dispatch_queue_attr_overcommit_unspecified) {
			DISPATCH_CLIENT_CRASH(tq, "Cannot specify an overcommit attribute "
					"and use this kind of target queue");
		}
	} else {
		if (overcommit == _dispatch_queue_attr_overcommit_unspecified) {
			// Serial queues default to overcommit!
			overcommit = dqai.dqai_concurrent ?
					_dispatch_queue_attr_overcommit_disabled :
					_dispatch_queue_attr_overcommit_enabled;
		}
	}
	if (!tq) {
		tq = _dispatch_get_root_queue(
				qos == DISPATCH_QOS_UNSPECIFIED ? DISPATCH_QOS_DEFAULT : qos,
				overcommit == _dispatch_queue_attr_overcommit_enabled)->_as_dq;
		if (unlikely(!tq)) {
			DISPATCH_CLIENT_CRASH(qos, "Invalid queue attribute");
		}
	}

	//
	// Step 2: Initialize the queue
	//

	if (legacy) {
		// if any of these attributes is specified, use non legacy classes
		if (dqai.dqai_inactive || dqai.dqai_autorelease_frequency) {
			legacy = false;
		}
	}

	const void *vtable;
	dispatch_queue_flags_t dqf = legacy ? DQF_MUTABLE : 0;
	if (dqai.dqai_concurrent) {
		vtable = DISPATCH_VTABLE(queue_concurrent);
	} else {
		vtable = DISPATCH_VTABLE(queue_serial);
	}
	switch (dqai.dqai_autorelease_frequency) {
	case DISPATCH_AUTORELEASE_FREQUENCY_NEVER:
		dqf |= DQF_AUTORELEASE_NEVER;
		break;
	case DISPATCH_AUTORELEASE_FREQUENCY_WORK_ITEM:
		dqf |= DQF_AUTORELEASE_ALWAYS;
		break;
	}
	if (label) {
		const char *tmp = _dispatch_strdup_if_mutable(label);
		if (tmp != label) {
			dqf |= DQF_LABEL_NEEDS_FREE;
			label = tmp;
		}
	}
	//申请和开辟内存
	dispatch_lane_t dq = _dispatch_object_alloc(vtable,
			sizeof(struct dispatch_lane_s));
	//构造函数 初始化
	_dispatch_queue_init(dq, dqf, dqai.dqai_concurrent ?
			DISPATCH_QUEUE_WIDTH_MAX : 1, DISPATCH_QUEUE_ROLE_INNER |
			(dqai.dqai_inactive ? DISPATCH_QUEUE_INACTIVE : 0));

	dq->dq_label = label;
	dq->dq_priority = _dispatch_priority_make((dispatch_qos_t)dqai.dqai_qos,
			dqai.dqai_relpri);
	if (overcommit == _dispatch_queue_attr_overcommit_enabled) {
		dq->dq_priority |= DISPATCH_PRIORITY_FLAG_OVERCOMMIT;
	}
	if (!dqai.dqai_inactive) {
		_dispatch_queue_priority_inherit_from_target(dq, tq);
		_dispatch_lane_inherit_wlh_from_target(dq, tq);
	}
	_dispatch_retain(tq);
	dq->do_targetq = tq;
	_dispatch_object_debug(dq, "%s", __func__);
	return _dispatch_trace_queue_create(dq)._dq;
}
```

同步任务的执行

**dq_width==1**

```c
DISPATCH_NOINLINE
void
dispatch_sync(dispatch_queue_t dq, dispatch_block_t work)
{
	uintptr_t dc_flags = DC_FLAG_BLOCK;
	if (unlikely(_dispatch_block_has_private_data(work))) {
		return _dispatch_sync_block_with_privdata(dq, work, dc_flags);
	}
	_dispatch_sync_f(dq, work, _dispatch_Block_invoke(work), dc_flags);
}
```

任务的封装，函数式  先存，CPU调度用的时候就取。

异步函数还有底层优先级的封装

